---
type: Workflow
title: Adding prompt text costs accuracy on fields the new text never mentions
description: The same schema change, described in 1618 characters of prose and then in 655, went from significantly worse than baseline to significantly better on a paired measurement. The loss and the gain both landed on unrelated fields, so the cost was the length rather than the content.
tags: [llm, prompts, evaluation, measurement, extraction]
generated: { by: claude/opus-5, at: 2026-08-12T16:20:00Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: depends-on, target: /meta/workflows/pair-both-arms-in-one-window-or-drift-picks-the-winner.md }
sources:
  - id: instrument
    resource: projects/k1/web/scripts/ab-paired.ts
    title: "Paired A/B, both arms interleaved per document in one serving window"
    last_modified: 2026-08-12
  - id: prompt
    resource: projects/k1/web/packages/ingestion/src/index.ts
    title: "K1_EXTRACTION_PROMPT, item J and Final K-1 paragraphs at 655 chars"
    last_modified: 2026-08-12
not:
  - term: "the edit only added instructions for new fields, so existing fields are unaffected"
    why: "measured twice, in both directions: the verbose version lost on boxes 1, 2, 5, 6a, 13, 18 and 20, none of which the new text mentions, and trimming it gained on the same boxes"
    instead: "A/B any prompt addition against the fields it does NOT mention, and treat total length as a variable in its own right"
  - term: "explaining WHY a field matters helps the model read it"
    why: "the tax rationale for each new field was what made the paragraph long, and it cost more elsewhere than it bought locally"
    instead: "state what to read and where it is printed; put the rationale in a code comment, where the reader who needs it will be"
  - term: "one paired run settles it"
    why: "two runs of an identical comparison on the same 60 documents returned p = 0.0078 and p = 0.0970, and a later comparison returned 5 discordant rows in one run and 76 in the next"
    instead: "run the comparison twice and pool the discordant counts, or treat a single marginal result as marginal"
---

# The observation

A schema change added Form 1065 item J's two columns, the Final K-1 checkbox, and
corrected three mislettered items. The prompt grew from 9931 to 11749 characters,
most of it explaining why each new field matters in tax terms.

Measured against the previous prompt, both arms interleaved per document in one
serving window: 38 rows fixed against 65 broken, p = 0.0101. Significantly worse.

The same schema, the same fields, the same JSON skeleton, with the prose cut from
1618 characters to 655: 66 fixed against 38 broken, p = 0.0078. Significantly
better.

Nothing changed except how much was said. Both movements landed on Part III boxes
the new text never mentions.

# Why it matters

The intuition that a prompt addition is locally scoped is wrong, and it is wrong in
the expensive direction. The new fields fed two validation checks. The boxes that
got worse hold the amounts the product exists to report. An unmeasured version of
this change would have traded the thing being sold for a diagnostic.

It also changes what a prompt comment is for. The tax rationale that made the
paragraph long is worth writing down, and the place for it is the code, where it
costs nothing at inference time. The prompt gets the layout and the field names.

There is a second, sharper lesson underneath. Compressing the Final K-1 sentence
took that checkbox from 4 wrong in 20 documents to 14 wrong in 20, so the short
prompt is not better at everything: it is better at Part III amounts and worse at
one checkbox. That is a trade to make deliberately rather than a version to call
correct. It was made by dropping the checkbox from the check that needed it and
reading item J instead.

# Evidence

Same comparison, same 60 documents, 624 truth rows, two prompt lengths:

```
  verbose  11749 chars   fixed 38  broke 65   p = 0.0101   worse
  trimmed  10786 chars   fixed 66  broke 38   p = 0.0078   better
```

Where the verbose version lost, by box. The new text mentions none of these:

```
  box 20  net -8      box 18  net -3
  box 6a  net -5      box 2   net -3
  box 5   net -4      box 13  net -3
                      box 1   net -3
```

Where the trimmed version gained, same boxes:

```
  box 20  net +11     box 17  net +4
  box 6a  net +6      box 1   net +3
```

On repeatability, the trimmed comparison was run twice against the same baseline:

```
  run 1   fixed 66  broke 38   p = 0.0078
  run 2   fixed 49  broke 33   p = 0.0970
  pooled  fixed 115 broke 71
```

The baseline's own absolute rate moved between those runs, 93.1% to 87.3% to 89.9%,
which is the serving drift the paired design exists to cancel and a reminder that
only the within-run comparison means anything.

# The effect is not linear in characters

A later edit went the other way and found nothing. Rewriting the item J paragraph to
ask for each cell as a verbatim string added 15 characters, taking the prompt from
10603 to 10606, and moved box accuracy not at all across two pooled paired runs:

```
  run 1   fixed  0  broke  5   p = 0.0625
  run 2   fixed 43  broke 33   p = 0.3019
  pooled  fixed 43  broke 38   not distinguishable from chance
```

So this is not a rule that any addition costs accuracy. 1818 characters of added
prose was measurable and 15 was not, which is the expected shape and worth stating
because the reflex after reading the section above is to fight over sentences.

# Why this is a k1 concept and not a meta practice

One model, one prompt, one corpus, one field family. The measured claim is about a
1818-character addition to a 10000-character document-extraction prompt, and
generalizing it to "keep prompts short" would apply a length preference everywhere
on evidence from a single system. Promote it when a second project measures the same
thing.

Related: [pair both arms in one window](../../../meta/workflows/pair-both-arms-in-one-window-or-drift-picks-the-winner.md)
is the instrument this depends on. Without it the verbose version's aggregate would
have been read as drift and shipped.
