---
type: Observation
title: Chris's M3 heat-set inserts are 5.04 mm OD by 4 mm long
description: Size insert holes for the on-hand M3 brass inserts at about 4.4 mm and at least 4.6 mm deep.
kind: stack
proposed_layer: project
proposed_project: 3d-printing
tags: [hardware, heat-set-inserts, m3]
generated: { by: claude/opus-5.5, at: 2026-09-26T19:33:42Z }
status: draft
sources:
  - id: generator
    resource: projects/3d-printing/collar/src/collar/boa_slot_gauges.py
    title: INSERT_HOLE_MM and the v4/v5 history in the docstring
    last_modified: 2026-09-26
---

# Observation

The M3 knurled brass heat-set inserts in Chris's assortment measure 5.04 mm OD and 4 mm long (caliper photo, 2026-09-26). The collar v5 coupon uses a 4.4 mm hole through a 4.6 mm base: 0.64 mm under OD, and a through hole so displaced plastic has somewhere to go.

The 4.4 mm hole is not yet print-verified. Update this once a v5 insert has been installed.

# Why it matters

The v4 coupon had 3.4 mm clearance holes through a 2.6 mm base, and the inserts could not be installed at all. Parts that will take inserts need both the right hole and enough material depth.

# Evidence

User report on v4: "the holes for the receiver are way too shallow and small. it's 5 mm in diameter ... and 4 mm in depth ... I was not able to use the gold inserts".
