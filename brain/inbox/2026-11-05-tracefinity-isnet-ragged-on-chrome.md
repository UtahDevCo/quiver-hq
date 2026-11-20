---
type: Observation
title: IS-Net leaves ragged edges on chrome tools; InSPyReNet traced them cleanly
description: On a polished nail clipper IS-Net cut into the reflective bottom edge (an undersized pocket); InSPyReNet followed it, with a little shadow at the hinge.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [tracefinity, tracing]
generated: { by: claude/opus-5.5, at: 2026-11-05T19:36:56Z }
status: draft
sources:
  - id: readme
    resource: https://github.com/tracefinity/tracefinity#local-models-default
    title: Tracefinity tracer table (IS-Net default; BiRefNet Lite for reflections)
---

# Observation

Same photo, same grid calibration. IS-Net traced the chrome nail clipper at
92.6 x 19.1 mm with a notch bitten out of the shiny lower edge. InSPyReNet gave
94.0 x 19.5 mm, following the edge but taking a little shadow at the hinge end
(slightly loose, the safe direction). On the gold razor the two agreed within 0.4 mm.
Matte black tools (straight razor, safety razor) traced cleanly on IS-Net.

Both tracers also picked up the notebook's spiral binding as a "tool" when it was
in the crop. Drop polygons by size and position before saving.

# Why it matters

A notch in the trace becomes a bump in the pocket wall, and the tool won't seat.

# Evidence

Overlays from runs/grid/PXL_20261105_180427460 (IS-Net) and runs/insp/PXL_20261105_180427460 (InSPyReNet), 2026-11-05.
