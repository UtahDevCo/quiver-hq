---
type: Failure Mode
title: A benchmark with no repeat run reports noise as a result
description: Comparing two prompts, models, or configs on one sample each produces a difference every time, and without a repeat run at fixed settings there is nothing to say whether that difference is larger than the measurement itself.
tags: [evaluation, benchmarks, llm, measurement, prompts]
generated: { by: claude/opus-5, at: 2026-08-11T00:07:35Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: depends-on, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
sources:
  - id: scorer
    resource: projects/k1/web/scripts/score-corpus.ts
    title: "k1 2489236 — score every fixture matching the current prompt hash and print the spread"
    last_modified: 2026-08-11
  - id: captures
    resource: projects/k1/data/stored-extractions
    title: "Two captures of 175 documents, one prompt, temperature 0: 94.7% and 97.4%"
    last_modified: 2026-08-11
  - id: wider-spread
    resource: projects/k1/data/stored-extractions
    title: "The same spread measured again a day later at 93.6% and 82.3%, so 2.7 points was not the ceiling"
    author: claude/opus-5
    last_modified: 2026-08-12
not:
  - term: "temperature is 0, so the run is reproducible"
    why: "temperature 0 fixes the sampling rule, not the serving stack; two identical runs came back 2.7 and 4.7 points apart, and on another day 11.3 apart"
    instead: "run the same config twice and treat the observed spread as the error bar on every comparison"
  - term: "the corpus is large enough that the rate is stable"
    why: "2125 scored boxes across 175 documents still moved 56 boxes between identical runs"
    instead: "size the sample against a measured spread, not against an intuition about n"
  - term: "the spread is now known, so a later comparison can be scored against a stored baseline"
    why: "knowing the noise floor tells you which effects are unmeasurable this way; it does not make the unpaired comparison valid for the ones that clear it"
    instead: "pair both arms in one window, and use the spread to decide whether the question is worth asking at all"
---

# The trap

Three prompt versions were measured against the same 175-document corpus, one
capture each, and read 95.5%, 94.8%, 94.7%. That ordering supported a whole story:
a cleanup had cost 0.8 points, the loss sat in boxes the change could not touch,
and the decline was monotone in prompt length across the three.

A fourth capture, at the prompt that produced 94.7%, with nothing changed,
returned 97.4%.

The gap between two identical runs was larger than the gap between any two
prompts. Every comparison made from the first three captures was a reading of the
measurement, and the monotone trend was three points on a line drawn through
noise.

The fix is not a bigger corpus. It is one repeat run at fixed settings, which
converts an unfalsifiable number into a number with an error bar, and costs
exactly one more sample.

# Why it matters

A single-sample benchmark cannot return "no difference". It always produces a
delta, the delta always has a plausible mechanism available, and the mechanism is
what gets written down and acted on. In k1 the story was prompt length diluting
attention on plain amount boxes, and the specific boxes that moved were the ones a
longer prompt would plausibly hurt. That explanation survived a per-box breakdown,
a coded-versus-plain split, and a check that the moved boxes had no relationship
to the edit.

None of those checks could fail, because all of them ran on the same single
sample.

The cost of the belief is what makes this worth recording. The number was days
from being handed to a co-founder as the quality bar for an ingestion pipeline,
and a prompt would have been reverted to recover 0.8 points that did not exist.

Temperature 0 is what made it feel settled. It fixes the sampling rule at the
decode step and says nothing about the serving stack underneath, which is free to
vary across capacity, routing, and revisions of the same model name.

# Evidence

Same 175 documents, same prompt hash `816eafddef1f`, same corpus, temperature 0,
one capture apart in time. Exact boxes out of 2125:

```
  budget 0     2013 (94.7%)  vs  2069 (97.4%)   2.7 points
  budget 2048  1953 (91.9%)  vs  2052 (96.6%)   4.7 points
```

Per box, the ones that carried the discarded story. Boxes 1, 6a, 6b, 9c and 10
hold a single amount and no code, so no version of the prompt edit could reach
them:

```
  box   n     v1    v2    v3    v3-again
  1     151   149   150   148   151
  6a    133   133   129   125   133
  6b    133   133   131   129   133
  9c     44    44    43    40    44
  10     44    44    44    42    44
```

The v1 to v3 column reads as a clean monotone decline. The fourth column is the
same configuration as the third.

What survived the repeat: the ranking of the worst boxes (18, then 19, then 20, in
both runs) and the direction of the budget comparison. Levels moved, order held,
which is the part of a noisy benchmark worth quoting.

The scorer now discovers every fixture whose recorded prompt hash matches the
current prompt, scores all of them, and prints the spread with the note that an
edit smaller than the spread is not measurable. One fixture prints no spread,
which is itself the signal that the number has no error bar yet.

# The floor is not a constant

The 2.7-point spread was measured on one day. Repeated the next day, the same
comparison of two identical captures read 93.6% and 82.3%, an 11.3-point spread.
A recorded noise floor is a sample of the noise, so treat it as the smallest
spread you have happened to observe rather than a bound.

That is what pushes the answer past "use a bigger error bar" and into
[pair both arms in one window](../workflows/pair-both-arms-in-one-window-or-drift-picks-the-winner.md).
An 11-point floor makes every prompt edit worth making unmeasurable by unpaired
comparison, no matter how large the corpus.

Related: [audits must report their own coverage](audits-must-report-their-own-coverage.md),
for the same reason — a rate printed without the thing that qualifies it reads as
more settled than it is.
