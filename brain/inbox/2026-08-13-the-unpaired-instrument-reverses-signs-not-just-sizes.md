---
type: Observation
title: An unpaired comparison reverses the sign, and does it twice out of two
description: Two claims measured unpaired at p = 8e-19 and p ~ 0 both flipped direction under the paired instrument, so an unpaired result carries no information about direction either.
kind: failure-mode
proposed_layer: meta
tags: [evaluation, benchmarking, confounds, drift, ab-testing]
generated: { by: claude/opus-5, at: 2026-08-13T15:16:43Z }
status: draft
sources:
  - id: paired-rasterize
    resource: projects/k1/data/paired-checks/2026-08-13-rasterize-the-upload.json
    title: Two paired runs of the rasterize-the-upload comparison
    last_modified: 2026-08-13
  - id: paired-skew
    resource: projects/k1/data/paired-checks/2026-08-12-skew-inside-a-pdf.json
    title: Two paired runs of the skew-inside-a-PDF comparison
    last_modified: 2026-08-12
  - id: instrument
    resource: projects/k1/web/scripts/ab-paired-input.ts
    title: The paired input comparison script
    last_modified: 2026-08-12
not:
  - term: "the unpaired run exaggerates the effect, so treat its direction as real and its size as inflated"
    why: "measured twice, both signs flipped: rasterizing read +8.0 points unpaired and -2.3 paired, and an item J prompt edit read 197 fixed / 15 broke unpaired against 0 fixed / 5 broke paired"
    instead: "take nothing from it, including the sign, and re-run paired before writing it down"
  - term: "a mechanism that explains the unpaired result is corroborating evidence"
    why: "the unpaired run credited rasterizing with removing code-letter confusion, and the paired runs show rasterizing causes it: box 20 lost 51 rows and gained 10"
    instead: "a mechanism story is as available for a drift artifact as for a real effect, so it raises confidence without raising accuracy"
---

# Observation

An unpaired A/B does not merely inflate an effect. It has now produced the wrong
sign twice out of two attempts, on the same provider, in the same week, with
p-values of 8e-19 and roughly 0.

```
                          unpaired              paired, pooled over 2 runs
rasterize the upload   +130 / -24   p=8e-19     +33 / -91 over 2654 rows
an item J prompt edit  +197 / -15   p~0         +43 / -38 over 81 discordant
```

The rasterization case is the sharper one, because the unpaired run did not just
get the size wrong. It named a mechanism, code-letter confusion falling from 16
occurrences to zero, and that mechanism is what the change actually damages: box
20, the code-plus-amount box, went 10 fixed against 51 broken across the two
paired runs, with boxes 19 and 18 next.

# Why it matters

The half-measure is what to guard against. Knowing that drift inflates effects
suggests a discount: keep the direction, halve the size, ship the change. Both
recorded cases would have shipped a change that made accuracy worse, and one of
them would have shipped a whole pipeline stage.

The p-value is worse than uninformative here, because it is computed over the
discordant count, and more drift means more discordant rows means a smaller
p-value. The number that reads as rigour is produced by the confound.

# Evidence

Two paired runs of the rasterization comparison, 103 documents, both arms adjacent
per document in one window, at the shipped prompt:

```
run 1   arm A 98.5%   arm B 96.2%   +14 / -44   p = 1.0e-4
run 2   arm A 98.3%   arm B 96.2%   +19 / -47   p = 7.6e-4
pooled                              +33 / -91
```

Both runs also agree on where it moves, which the unpaired run got backwards:

```
        run 1        run 2
box 20  +4  -24      +6  -27
box 19  +3  -6       +3  -8
box 18  +5  -8       +5  -9
box 8   +2  -0       +2  -0
```

The same session, same instrument, on the skew question: 0 fixed / 7 broke and
0 fixed / 6 broke over 127 rows, so the paired instrument is reproducible here
even where the unpaired one was not.

One further reading, from the arms themselves rather than the comparison: arm A
read 100.0% on the 12 degraded documents in both skew runs, while a stored capture
of those same 12 documents at an earlier prompt read 83.5%. 16 points on an
identical document set, which is larger than either effect under test.

# Where this belongs

This refines two existing meta concepts rather than standing alone:

- `meta/workflows/pair-both-arms-in-one-window-or-drift-picks-the-winner.md` gains
  a second confirmed sign reversal and the "keep the direction, discount the size"
  temptation as a `not:` entry.
- `meta/failure-modes/a-measurement-must-use-the-input-container-production-uses.md`
  has an open question in its "What this experiment did NOT establish" section,
  asking whether re-encoding the input helps at all. It is now answered: no, it
  costs 2.3 points, and the section can say so instead of asking.
