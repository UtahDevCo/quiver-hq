---
type: Failure Mode
title: A synthetic corpus cannot measure a failure its generator has no state for
description: If the generator always populates a field, extraction can never be scored on what it does when the field is blank, and the rate reads perfect on the one case that matters.
tags: [testing, evaluation, synthetic-data, extraction, coverage]
generated: { by: claude/opus-5, at: 2026-08-12T17:43:04Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: depends-on, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
sources:
  - id: commit
    resource: projects/k1
    title: "1d42062 feat(scripts): check item J's two columns against the column they are printed in"
    last_modified: 2026-08-12
  - id: measurement
    resource: projects/k1/web/scripts/verify-real-k1s.ts
    title: Column-aware item J check against the PDF text layer
    last_modified: 2026-08-12
not:
  - term: "the corpus rate is high, so the field is read correctly"
    why: "the rate only covers input states the generator emits; a state it never emits is unmeasured, not passing"
    instead: "list the input states the field can take in the wild, then check which of them the generator ever produces"
  - term: "add more documents to the corpus"
    why: "more samples of the same generator produce more of the same states and move the rate by noise"
    instead: "score a handful of real documents, which is where absent, malformed and out-of-schema states actually live"
  - term: "the value appears on the source document, so it was read correctly"
    why: "a value copied from the adjacent column is on the page, in the right row, and of the right magnitude; only its position falsifies it"
    instead: "check the field against the position it is printed in, not against the set of values printed anywhere"
---

# The trap

A generated evaluation corpus measures a field only across the input states its
generator produces. Where the generator is uniform, the rate for that field is
high and says nothing.

Concretely: a two-column form field (Beginning / Ending) scored 99.8% across 1050
cells of a 175-document synthetic corpus. On four real documents it scored 83.3%
of 24 cells. Every error was one mistake the generator cannot produce, because it
writes both columns on every document it renders. Real forms leave the Beginning
column blank for a first-year holder, and the extractor filled it by copying the
Ending figure across.

The diagnostic question is not "how large is the corpus" but "which input states
does the generator emit for this field". Enumerate the states the field can take
(populated, blank, zero, out-of-schema literal), then check the generator against
that list. Anything it never emits is unmeasured.

# Why it matters

The failure is worse than an unmeasured gap, for two reasons.

The invented value is indistinguishable from a correct one downstream. It is a
number that appears on the document, in the right row, of the right magnitude.
A validator asking "does this figure appear on the page" confirms it. Only column
position falsifies it, and by the time the value is in the record that is gone.

And the high rate actively suppresses investigation. 99.8% is the number you
quote to argue the field is finished and move on. The gap between a corpus rate
and a real-document rate on the same field is the measurement worth having, and
it only exists if someone scores real documents at all.

A third state showed up in the same four documents: a tiered partnership printing
`VARIOUS%` where a percentage belongs. The extractor correctly returned null, and
the schema had nowhere to record that the value varied, so the fact was silently
dropped rather than stored wrong. A generator emitting only well-formed values
cannot surface that either.

# Evidence

The generator's uniformity, and the failure it hides:

```
2023 real K-1   Profit  printed [0.010548, 0.010373]  extracted [0.010548, 0.010373]   ok
2022 real K-1   Profit  printed [blank,    0.010548]  extracted [0.010548, 0.010548]   copied across
2022 real K-1   Capital printed [blank,    blank]     extracted [0.010548, 0.010548]   invented both
2025 real K-1   Profit  printed [VARIOUS,  VARIOUS]   extracted [null,     null]       unrepresentable
```

Rates on the same field, same prompt, same model:

```
synthetic corpus   1048 / 1050 cells   99.8%
real documents        20 /   24 cells   83.3%
```

The check that found it compares each cell against the column it is printed in,
using `pdftotext -layout` character offsets, rather than asking whether the value
appears anywhere on the page. The earlier amount sweep passed 144/144 on the same
four documents and could not have caught this: it excluded percentage paths, and
the invented figure is printed on the page regardless.

# The follow-up, because the obvious fix did not work

Once the state is known, the reflex is to describe it in the prompt. That was
tried three ways: naming the blank case, forbidding the copy explicitly, and
changing the schema to ask for each cell as a verbatim string of exactly what is
printed. The model produced identical output under all three, and kept copying
across.

Only one of the two problems yielded to instruction. The verbatim-string schema
does capture the `VARIOUS` state that was previously unrepresentable, which is a
real information gain. The invented cell needed a coherence rule downstream: a
positive beginning capital share against a printed beginning balance of nothing
plus a contribution during the year is a partner who was admitted mid-year, and
the share cannot exist. That rule fires on exactly the one real document and stays
quiet on the other three.

So the value of finding the unmeasured state is not that it tells you what to
write in the prompt. It is that it tells you which downstream check has to exist,
because the extractor is not going to stop.

Related: [audits must report their own coverage](audits-must-report-their-own-coverage.md)
is the same distinction one level up, where a skipped check is reported as a pass.
