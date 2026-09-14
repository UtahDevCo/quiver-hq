---
type: Module
title: QIDI Plus 4 hardware profile (enclosed CoreXY, actively heated chamber)
description: Enclosed CoreXY, 305×305×280 mm, direct-drive bimetal hotend to 370°C, bed to 120°C, 400W chamber heater to 65°C, dual textured PEI, Klipper + QIDI Studio.
kind: module
tags: [3d-printing, hardware, qidi, printer, reference]
generated: { by: claude/opus-4-8, at: 2026-09-13T20:39:11Z }
verified:
  - { by: human:christopher, at: 2026-09-14T19:48:30Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: qidi-techspecs
    resource: https://qidi3d.com/pages/qidi-plus-4-techspecs
    title: QIDI Plus 4 official tech specs
    last_modified: 2026-09-13
  - id: qidi-review
    resource: https://qidi3d.com/blogs/news/qidi-plus-4-3d-printer-review
    title: QIDI Plus 4 review (chamber heater, per-material notes)
    last_modified: 2026-09-13
  - id: 3dput-review
    resource: https://3dput.com/qidi-plus4-review-the-heated-chamber-powerhouse-for-engineering-filaments/
    title: 3DPut Plus 4 review (bimetal direct-drive, practical speeds)
    last_modified: 2026-09-13
---

# Module

The 3D printing hardware Chris runs. This is the machine every collar TPU/PETG
print targets, so its limits set what the CAD tooling can assume.

| Spec | Value |
|---|---|
| Architecture | Enclosed **CoreXY** (9mm 1.5GT belts) |
| Build volume | **305 × 305 × 280 mm** |
| Hotend | **Bimetal, direct-drive**, 80W, max **370°C** |
| Bed | 6mm aluminum, **max 120°C**, dual-sided **textured PEI** (magnetic flex plate) |
| Chamber | **Actively heated, 400W, up to 65°C**, ~5–8 min to temp |
| Speed / accel | 600 mm/s marketing; **200–300 mm/s practical**; ≤20,000 mm/s² |
| Nozzle | **0.4mm bimetal** stock (0.2 / 0.6 / 0.8 options); hardened-steel extruder gears |
| Firmware / slicer | **Klipper** (Fluidd/Moonraker web UI), input shaping + pressure advance; slices in **QIDI Studio** (Orca / PrusaSlicer also work) |

The active heated chamber and 370°C direct-drive hotend are the distinguishing
features: this is an engineering-filament machine, not a hobby PLA box. See
[[plus-4-chamber-heat-off-for-pla-and-tpu]] for how the chamber changes
per-material handling.

# Why it matters

The build volume (305×305×280) is the hard ceiling on any single-piece collar
part. The direct-drive extruder is why TPU prints at all here. The chamber and
120°C bed are what make PETG/PETG-CF viable without warping.

# Notes

Minor source conflicts, resolved: one review listed the bed max as 100°C, but
QIDI's spec sheet says **120°C** (trust QIDI). QIDI's spec says **bimetal**
hotend; a third-party page's "all-metal" is loose wording.
