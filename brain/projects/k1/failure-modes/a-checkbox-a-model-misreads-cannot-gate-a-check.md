---
type: Failure Mode
title: A boolean read off a form is the least reliable field on it, so never let one gate a check
description: A validation rule was gated on a newly extracted checkbox. Across three prompt revisions the extractor read that box wrong on 4, 14 and 13 of the same 20 documents, moving with wording that had nothing to do with checkboxes. The rule was rewritten to read two numbers that say the same thing.
tags: [llm, extraction, validation, measurement, checkboxes, vision-models]
generated: { by: claude/opus-5, at: 2026-08-12T16:25:00Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: instance-of, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
sources:
  - id: check
    resource: projects/k1/web/packages/db/src/k1-coherence.ts
    title: "redeemedPartnerWarnings — reads item J's two columns, not the Final K-1 checkbox"
    last_modified: 2026-08-12
  - id: measurement
    resource: projects/k1/data/stored-extractions/2026-08-12-gemini-2.5-flash-f55283cd-defects.meta.json
    title: "Three captures of 20 documents: checkbox reported checked 7, 17, 16 times where 3 are printed checked"
    last_modified: 2026-08-12
not:
  - term: "the extractor returns the field, so a check can read it"
    why: "presence in the schema says nothing about accuracy, and a field added an hour ago has no measured error rate at all"
    instead: "measure a new field against the source documents before writing anything that branches on it"
  - term: "checkboxes are the easy part, the amounts are what's hard"
    why: "a small empty box carries almost no visual signal; the model inferred a checked box from redemption-shaped amounts nearby"
    instead: "treat every boolean read off a form as the least reliable field on it"
  - term: "tighten the prompt so it reads the checkbox properly"
    why: "an instruction naming the true condition made it worse, 4 wrong in 20 to 14 wrong in 20, by priming the value it described"
    instead: "find two numbers on the form that imply the same fact and read those"
  - term: "lower the severity so a false positive is cheap"
    why: "an info firing on a fifth of documents buries the ones that are real, which is the same outcome as no check"
    instead: "make the rule stand on evidence that does not need the unreliable field"
---

# The trap

A schema change added the Form 1065 "Final K-1" checkbox, and a rule went in on top
of it the same hour: a final K-1 whose capital account still shows a balance is a
redemption nobody closed out. Sound tax logic, and it caught the corpus defect it
was written for.

The checkbox itself was wrong on 4 of 20 documents, so the rule was about to fire on
a fifth of production. Two attempts to fix that failed and one worked.

Prompting harder made it worse. Adding "a field ending in _checked is true only
where a mark is printed in or beside that box, an empty box is false" took it from 4
wrong to 14 wrong: naming the true condition primed the model to claim it, and it
reported checked on 17 of 20 forms where 3 are checked.

Corroborating it was better but not enough. Requiring item J's ending capital share
to be 0 before firing filtered 13 of 16 false claims, and one survived: a
guaranteed-payment partner whose item J prints 0% in both columns beside a 200000
capital account. The checkbox was misread there and the gate passed legitimately.

What worked was dropping the checkbox. Item J states the same fact in numbers: a
capital share that falls from something to nothing IS a partner who was bought out.
Requiring a positive beginning share and a zero ending share is what separates a
partner who left from one who never held anything, which is exactly the case that
defeated the corroboration version.

# Why it matters

The failure is asymmetric. A missed defect costs one document. A check gated on a
field with a 20% error rate costs a fifth of every document forever, in reviewer
attention, which is the one resource a validation layer exists to spend well.

The general shape: when a check reads two fields and compares them, a field that
gates whether the check runs at all passes its error rate straight through to the
false positive rate, with no arithmetic in between to absorb it. Gating fields need
more evidence than compared fields.

And the reliability was not a property of the model alone. It moved from 4-in-20 to
14-in-20 across prompt revisions whose edits were about item J, not checkboxes. A
field whose accuracy swings with unrelated wording cannot be depended on by
anything, which is a stronger reason to route around it than any single
measurement.

# Evidence

The same 20 documents, three prompt revisions, against the printed box (3 are
checked):

```
  b1a18785   reported checked  7    wrong  4/20
  d12185be   reported checked 17    wrong 14/20
  f55283cd   reported checked 16    wrong 13/20
```

Why corroboration alone was not enough. The claimed-final documents at the shipped
prompt, gated on item J's ending capital share:

```
  document  really final?  J capital end  L capital end   verdict
  D14       yes            0              150000          fires, correct
  D13       yes            0              113105          fires, correct
  D10       NO             0              200000          fires, WRONG
  D01       NO             55             -653254         filtered
  D18       NO             67             206705          filtered
  ...       NO             20 to 60       various         filtered
```

D10 is the case that forced the redesign: its item J really does print 0% ending, so
no corroboration on the ending column alone can save the rule. Requiring a positive
BEGINNING share filters it, and needs no checkbox at all.

# Why this is a k1 concept and not a meta practice

The evidence is one checkbox, on one form, read by one model, across three revisions
of one prompt. The mechanism looks general and the sample does not support saying
so. Two things would lift it: the same swing measured on a different boolean field,
or a second repo where an LLM-extracted flag gated a rule.

Related: [audits must report their own coverage](../../../meta/failure-modes/audits-must-report-their-own-coverage.md)
is the same distinction one level up. Here the could-not-check case is item J blank,
and it is reported as a miss rather than a pass.
