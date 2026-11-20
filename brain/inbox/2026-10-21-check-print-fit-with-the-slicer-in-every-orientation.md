---
type: Observation
title: Check print fit with the slicer's arrange, in the orientation the designer exported
description: A hand fit check that only lays each part on its largest face called VAULT L modules unprintable on a 305 mm bed; the designer had exported them upright and pre-rotated 45°, and they fit.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [3d-printing, print-fit, stl, slicer]
generated: { by: claude/opus-5.5, at: 2026-10-21T18:30:00Z }
status: draft
sources:
  - id: manifest
    resource: projects/tools/3d/vault/README.md
    title: VAULT build manifest, Build section (correction) and sliced job table
    last_modified: 2026-10-21
  - id: slicer
    resource: projects/tools/3d/slicer/slice-job.ts
    title: headless QIDI Studio slice with arrange and fit report
    last_modified: 2026-10-21
not:
  - term: "measure along the part's own axes, lay it on its largest face, and compare to the bed"
    why: "drops every upright and diagonal orientation; VAULT L5 Module 1F (329.7 x 230.1 x 57.7) fails that test but prints standing on its 329.7 x 57.7 face, rotated 45° into a 268 x 268 mm square, 230.1 mm tall"
    instead: "slice the file as exported with arrange on (--orient 0) and read placement from result.json; only then try other orientations"
  - term: "a tilted or off-axis STL is an export mistake to normalize away"
    why: "print-ready files are often exported in their intended print pose; VAULT modules and roofs ship upright, and the L parts ship pre-rotated 45° to fit a ~300 mm bed"
    instead: "treat the exported pose as the designer's intended print orientation until the slicer says otherwise"
---

# Observation

Before declaring a part too big for the printer, run it through the slicer's arrange in the
orientation the file was exported. Manual fit checks that test one orientation (largest face down)
miss the upright and diagonal poses designers use to fit long parts on a square bed.

# Why it matters

A false "doesn't fit" changes the design. On 2026-10-20 the VAULT tool chest was redesigned from
L width (three L 1F drawers over an S+S 2F pair) to all M width, losing the side-by-side 2F
drawers, on the strength of a wrong fit check. The slicer placed an L5 module and an L5 grid roof
on a single Plus 4 plate the next day.

# Evidence

Raw axis-aligned extents of the exported files: M5 Module 1F 253.9 × 57.0 × 230.1 (upright);
old-release L5 Module 1F 268.2 × 268.2 × 230.1 (upright, rotated 45°). QIDI Studio CLI,
2026-10-21: L5 Module 1F sliced onto one plate, bbox x 18.4–286.6, y 18.4–286.6, 230.1 mm tall,
15.4 h, 490 g; L5 Grid Roof bbox 32.4–272.6 square, 230.0 mm tall.
