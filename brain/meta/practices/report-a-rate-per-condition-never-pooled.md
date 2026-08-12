---
type: Practice
title: Report a degradation rate per condition, never pooled
description: Three input degradations averaged to 77.4%; separately they were 92.1%, 92.1% and 48.0%, and only the split identifies which one to look at.
tags: [evaluation, metrics, reporting, extraction]
generated: { by: claude/opus-5, at: 2026-08-12T17:43:04Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: depends-on, target: /meta/failure-modes/a-measurement-must-use-the-input-container-production-uses.md }
sources:
  - id: commit
    resource: projects/k1
    title: "9fcbee3 feat(scripts): measure the degraded subset, and find that skew is the whole cost"
    last_modified: 2026-08-12
  - id: fixture
    resource: projects/k1/data/stored-extractions/2026-08-12-gemini-2.5-flash-f55283cd-degraded.meta.json
    title: Degraded capture sidecar, recording the per-variant split and why not to quote the pooled rate
    last_modified: 2026-08-12
not:
  - term: "the pipeline scores 77.4% on scanned documents"
    why: "no condition scores near 77.4%; it is the midpoint of two populations and describes neither"
    instead: "quote each condition, and name the input container the measurement used"
  - term: "compare the subset rate to the full corpus average"
    why: "that compares document sets as well as conditions; 9 of an apparent 12.3-point gap was the documents"
    instead: "score the same documents under both conditions and report the paired difference"
  - term: "report accuracy per condition and stop there"
    why: "a condition the system reads badly but flags loudly is a different product problem from one it reads badly and passes"
    instead: "split detection alongside accuracy: misread, and misread-without-a-warning"
---

# The practice

When an evaluation varies an input condition, report the rate per condition and do
not publish the pooled figure. Pooled, you get a number no condition exhibits.

Three degradations of the same 12 documents, one model, one prompt:

```
200 DPI raster            92.1% exact
200 DPI JPEG quality 45   92.1% exact
200 DPI rotated 1.5 deg   48.0% exact, all 12 documents misread
```

Pooled: 77.4%. That figure supports "scans cost us about six points", which is
wrong twice over. Two of the three conditions cost nothing measurable, and the
third looked catastrophic.

Hold the sample fixed too. Comparing this 12-document subset against the
175-document corpus average showed a 12.3-point gap, of which 9 points was the
documents rather than the condition.

# Why it matters

A pooled rate points at the wrong fix. Two of the three conditions needed no work
at all.

The split also made a follow-up question askable that the average hid. Once the
48.0% stood alone it was obviously anomalous, which is what prompted checking it
against the input shape production actually accepts. Wrapping the identical
rasters in a PDF moved the three conditions to 100%, 100% and 92.9%: the collapse
was an artifact of submitting a bare image, and the pooled 77.4% had averaged a
real result together with an artifact. See
[measure through the input container production accepts](../failure-modes/a-measurement-must-use-the-input-container-production-uses.md).

So the per-condition split is not only a reporting preference. It is what makes an
implausible cell visible while it can still be chased.

Pair the accuracy split with a detection split, because a bad rate is survivable
if the system knows. 11 of the 12 rotated documents raised a validation warning,
so even the anomalous condition was loud rather than silent.

# Evidence

Reproducible offline from committed fixtures:

```
bun run score --ledger <degraded>.jsonl --variant rot1.5deg
bun run score --ledger <clean>.jsonl   --only <the same 12 names>
bun scripts/score-defects.ts --clean-ledger <degraded>.jsonl --variant rot1.5deg
```

Per condition, accuracy against documents-flagged:

```
condition          exact   read perfectly   misread   misread flagged
200 DPI raster     92.1%        9 / 12          3            1
JPEG q45           92.1%        9 / 12          3            2
rotated 1.5 deg    48.0%        0 / 12         12           11
```

`--variant` and `--only` exist in both scorers so the split is a flag rather than
a one-off shell pipeline, and the capture sidecar records "Do NOT quote the 77.4%
pooled rate" beside the fixture that produced it.

Putting the mechanism in the tool rather than in a reviewer's memory is the part
that survives: a pooled rate is what you get by default from any scorer that
accepts a mixed ledger, so the filter has to be as cheap as not using it.
