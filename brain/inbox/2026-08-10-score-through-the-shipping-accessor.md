---
type: Observation
title: Score accuracy through the accessor that ships, not a harness replica
description: An eval harness that reads the model output more permissively than production turns a data-loss bug into a reported win.
kind: failure-mode
proposed_layer: meta
tags: [evaluation, extraction, measurement, llm]
generated: { by: claude/opus-5, at: 2026-08-10T16:03:58Z }
status: draft
sources:
  - id: fix
    resource: projects/k1
    title: "k1 e88ffbb — fix(db): read coded box amounts from both places the prompt declares"
    last_modified: 2026-08-10
  - id: production-accessor
    resource: projects/k1/web/packages/db/src/k1-canonical.ts
    title: codedItemsFromGoogle, which read only the flat box_NN_codes sibling
    last_modified: 2026-08-10
not:
  - term: "score the model's raw JSON with a hand-written path reader"
    why: "the reader drifts toward permissive, because every near-miss you decide to credit is a one-line change in the harness and nobody reviews the harness"
    instead: "import the production normalizer and assert on what it returns, so the metric cannot credit a value the pipeline discards"
---

# Observation

When measuring extraction accuracy, score the object the pipeline stores, by calling the
production normalizer. A separate path reader written for the eval will read more
generously than production, and the difference is invisible: every number improves, no test
fails, and the gap is exactly the data your users lose.

In k1 the extraction prompt declared two homes for every coded box on a Schedule K-1: a
`codes` object nested in the box, and a flat `box_NN_codes` sibling. Production's
normalizer read only the sibling. The eval harness merged both. So 53 codes across 9 of 175
documents were extracted correctly, credited as correct, and dropped before the database.
Scored through the real normalizer, box accuracy was 93.4% and not the 95.5% that had been
reported and acted on.

# Why it matters

Every downstream decision was made on the wrong number. A thinking-budget comparison, a
disagreement gate calibration, and the choice of which boxes to work on next were all
scored against an accessor more forgiving than the shipping one. The ordering survived
here, which is luck: the gap was 2.1 points on one arm and 2.4 on the other, so a decision
resting on a 2-point margin would have gone the wrong way and looked well-measured doing
it.

The loss also degraded quietly rather than loudly. Most dropped entries kept the amount and
lost the letter, and on a K-1 the letter is what selects the tax treatment. A missing box
reads as missing; a box with the right money and no code reads as populated.

Two accessors over one record is the smell, and it does not matter that one of them lives
in test code. Grep the field name and count the readers.

# Evidence

Production, before the fix, at `packages/db/src/k1-canonical.ts`:

```ts
const codeMap = readPath(input.data, input.codesPath); // "part_iii.box_14_codes" only
```

The eval harness, merging the map production ignored into the one it read:

```ts
const codeMap = {
  ...(at(data, `${paths.box}.codes`) ?? {}),   // production never reads this
  ...(paths.codes ? (at(data, paths.codes) ?? {}) : {}),
};
```

Re-scoring the same 350 stored extractions, once with the harness reader and once by calling
`normalizeGoogleK1Output` and asserting on `normalizedK1.boxes`:

| accessor | budget 0 | budget 2048 |
| --- | --- | --- |
| harness (merged) | 95.5% | 92.1% |
| production (sibling only) | 93.4% | 89.6% |

The defect surfaced from an unrelated direction. A cross-budget disagreement report printed
the path `part_iii.box_14_codes.A` as present in one arm, which could not be reconciled with
the same run's claim that code 14A was null. One of the two had to be reading a different
map. Neither the 602-test suite nor the accuracy metric had anything to say about it.

Related: [[audits-must-report-their-own-coverage]],
[[fixing-the-write-path-does-not-fix-the-written-rows]] (the rows written under the old read
are still short those codes).
