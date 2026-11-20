---
type: Observation
title: Lightning infill bows hollow double-walled parts; keep a tying infill in them
description: A VAULT L5 module printed with 8% lightning infill came out with its 330 mm top and bottom panels bowed inward by several millimetres; grid infill ties the two skins of a double wall, lightning does not.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [3d-printing, infill, lightning, warping, pla]
generated: { by: claude/opus-5.5, at: 2026-10-22T06:00:00Z }
status: draft
sources:
  - id: manifest
    resource: projects/tools/3d/vault/README.md
    title: VAULT manifest, print folder section (lightning infill tried and rejected)
    last_modified: 2026-10-22
  - id: profile
    resource: projects/tools/3d/slicer/profiles/vault-pla-light.json
    title: vault-pla-light profile with its do-not-use note
    last_modified: 2026-10-22
not:
  - term: "switch to lightning infill to cut weight; it is close to 0% infill and the walls carry the load"
    why: "in a hollow double wall the infill is what ties the two skins into one stiff section; without it each skin is a thin membrane that shrinks and bows as long layer lines cool"
    instead: "keep a connecting infill (grid, gyroid) in parts built from double walls; save weight elsewhere, or on solid-floored parts printed flat"
---

# Observation

Slicer weight estimates make lightning infill look like a free saving: on VAULT parts it landed
within 2 g of 0% infill and cut module weight 23% and print time about 40%. On a part whose panels
are hollow double walls, that saving comes from removing the material that keeps the panel flat.

# Why it matters

The test L5 Module 1F (QIDI Plus 4, generic PLA, 0.20mm Standard with 8% lightning, printed
upright, 9.76 h, 378 g) came out with both 330 mm panels bowed inward by several millimetres.
Pushed flat, they sprang back, so the bow was printed in, not flex. The drawer box rides between
those panels, so the part was scrap: 9.8 hours and 378 g lost, and the build went back to the
designer's standard 15% grid (4.56 kg instead of 3.78 kg).

# Evidence

Printer job history: `vault-W3-L5-module-1F-light-test.gcode`, completed 2026-10-21 22:39,
131,018 mm filament. Same module at 15% grid slices to 490 g / 15.4 h. With 2 walls at 0.45 mm,
each skin is about 0.9 mm thick. Photo shared in session 2026-10-22 showing both panels bowed
toward the centre.
