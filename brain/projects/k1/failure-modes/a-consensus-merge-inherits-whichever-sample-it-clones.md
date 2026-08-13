---
type: Failure Mode
title: A consensus merge inherits the quality of whichever sample it clones
description: Anchoring the merge on the first sample scored 93.1% against 95.2% for anchoring on the sample that agrees most with the others, and at n=2 the merge scored exactly the primary's own rate.
tags: [llm, sampling, consensus, evaluation, measurement]
generated: { by: claude/opus-5, at: 2026-08-11T00:00:00Z }
status: stable
stale_after: 2027-08-13
sources:
  - id: consensus
    resource: projects/k1/web/packages/ingestion/src/k1-consensus.ts
    title: "k1 267dab8 — consensusK1 picks its anchor by agreement rather than by position"
    last_modified: 2026-08-11
  - id: scorer
    resource: projects/k1/web/scripts/score-consensus.ts
    title: "Offline measurement of merge accuracy and error density by dispute depth"
    last_modified: 2026-08-11
not:
  - term: "sample 0 is the primary, so clone it and override the disputes"
    why: "the clone supplies structure, every ignored field, and any field with no plurality, so a bad sample in that seat drags the merge down to itself; it cost 2.5 points and at n=2 the merge scored exactly the primary's rate"
    instead: "pick the anchor by counting how often each sample matches the others, which needs no labels"
  - term: "more samples is monotonically better"
    why: "n=2 read 84.7% and n=3 read 90.7% against n=4's 95.2%, because at the lower counts the degraded samples were half or more of the pool"
    instead: "report the rate at every sample count you can form, and expect non-monotonicity when sample quality is correlated within a batch"
  - term: "row accuracy went up, so the review queue got shorter"
    why: "the merge raised rows from 93.6% to 95.2% while clean documents FELL from 143 to 134, because it fixes scattered rows across many documents"
    instead: "quote the per-document clean rate when the consumer is a review queue, since review is per document"
---

# The trap

Sampling one model N times and merging the results needs a base record: something has
to supply the fields the comparison does not vote on, and the fields where no value
wins a plurality. The obvious base is the first sample. That makes the merge's
accuracy a function of which sample happened to be first.

Measured over 175 documents with 4 samples each, half of them from a serving window
that had degraded: anchoring on the first sample scored 93.1%, and anchoring on the
sample that agreed most with the others scored 95.2%. At n=2 the first-sample merge
scored 84.7%, which is the primary sample's own rate to within a rounding step,
because a rule that only overrides on a plurality can almost never override with one
other opinion.

A degraded sample is degraded by disagreeing. Counting, for each sample, how many of
its fields match the other samples ranks them without any labels, and the winner takes
the anchor.

# Why it matters

The failure is invisible in the aggregate. The merge still beat the average sample,
the code had a test, and the number went up. Nothing pointed at the anchor. It
surfaced because the fixtures were enumerated in alphabetical order, a rename put the
bad capture first, and the same script returned a different answer. An ordering that is
arbitrary at the call site became load-bearing inside the merge, and every measurement
taken under one ordering silently assumed it.

It also sets the ceiling on what sampling can do. 14 of 102 residual errors were rows
where all four samples agreed and all four were wrong. No sample count reaches those,
and a plan to "add more runs until it's accurate" spends without bound on them. They
need a deterministic check or a different prompt.

# Evidence

Same 175 documents, same prompt, 4 samples each (two captures x two thinking budgets),
scored through the shipping accessor against generator sidecars.

```
  each sample alone       82.3%   82.7%   91.0%   93.6%
  merge, anchor = first   93.1%
  merge, anchor = most agreeing   95.2%
```

Error density by how lopsided each disagreement was, at n=4, over 2125 rows:

```
  all 4 agree      1324 rows    5 errors    0.4%
  leader 3 of 4     360 rows    9 errors    2.5%
  leader 2 of 4     191 rows   56 errors   29.3%
  leader 1 of 4     250 rows   32 errors   12.8%
```

A single dissenting sample is close to no signal at all: 2.5% against the 0.4% floor.
Treating every disagreement as a flag marks 35% of rows. Marking only the leaders at or
below half the samples marks 20.8% and still contains 88 of the 102 errors.

# Related

[measure-the-noise-floor-before-ranking-two-prompts](../../../meta/failure-modes/measure-the-noise-floor-before-ranking-two-prompts.md)
is why there were four samples to merge in the first place.
[self-reported-confidence-is-not-a-signal](../../../meta/failure-modes/self-reported-confidence-is-not-a-signal.md)
is the contrast: agreement across samples carries the signal that a model's own
confidence does not.
