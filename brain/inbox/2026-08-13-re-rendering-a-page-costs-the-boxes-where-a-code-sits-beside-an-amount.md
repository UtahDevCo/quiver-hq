---
type: Observation
title: Re-rendering a page costs the fields where two values sit side by side
description: Rasterizing a digital K-1 lost 51 of 61 discordant rows in box 20 alone, the box where a code letter is printed beside its amount, while single-value boxes barely moved.
kind: failure-mode
proposed_layer: project
proposed_project: k1
tags: [extraction, multimodal, ocr, k1]
generated: { by: claude/opus-5, at: 2026-08-13T15:16:43Z }
status: draft
sources:
  - id: paired-runs
    resource: projects/k1/data/paired-checks/2026-08-13-rasterize-the-upload.json
    title: Two paired runs, per-box movement
    last_modified: 2026-08-13
not:
  - term: "a 200 DPI raster is legible to a human, so it is legible to the model"
    why: "the amounts survive; the association between a code letter and the amount printed next to it is what degrades, and a human reading the same raster reconstructs that association from layout without noticing they are doing it"
    instead: "score the paired fields separately from the single-value fields, because a pooled rate hides a loss concentrated in one box type"
---

# Observation

Rasterizing a digital K-1 at 200 DPI and rewrapping it as a PDF costs accuracy,
and the cost is not spread across the form. Pooled over two paired runs of 103
documents:

```
box 20   +10  -51      code letter beside an amount, several rows per box
box 19   +6   -14      code letter beside an amount
box 18   +10  -17      code letter beside an amount
box 8    +4   -0       a single amount
everything else        within 1 or 2 rows of zero
```

Boxes 18, 19 and 20 are the three Part III boxes that print a code letter next to
each amount, often several rows deep in one box. They account for 82 of the 91
broken rows. Single-amount boxes are unaffected, and box 8 is the only consistent
improvement, in both runs, by 2 rows.

# Why it matters

It shapes what to measure and what to check. A pooled exact rate moves 2.3 points
and reads as a mild regression, while the boxes that carry tax treatment lose
several times that. In k1 a wrong code letter on a right amount is the failure that
no arithmetic check catches, which is already tracked separately on the accuracy
page as "right number, wrong letter".

The practical consequence: any change to how a document is rendered before
extraction has to be scored per box type, and the code-plus-amount boxes are the
ones that decide it.

# Evidence

The two paired runs, both arms adjacent per document, at prompt 8af55a98b03c:
`data/paired-checks/2026-08-13-rasterize-the-upload.json`. Per-box movement is
printed by `web/scripts/ab-paired-input.ts` under "where it moved".

Related, and the reason to keep this as a k1 concept rather than a general one:
the same three boxes are where an earlier prompt-length experiment moved, and
where the corpus generator's coverage is thinnest. Whether the finding is about
raster quality or about this form's layout is not established by one form type.
