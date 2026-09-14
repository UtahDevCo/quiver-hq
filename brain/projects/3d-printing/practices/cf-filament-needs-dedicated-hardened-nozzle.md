---
type: Practice
title: Keep a dedicated hardened nozzle for PETG-CF, and one nozzle per material family
description: Carbon-fiber filament is abrasive and wears even the bimetal stock nozzle; a hardened nozzle is effectively mandatory for PETG-CF. Swapping materials on one nozzle also causes clogs.
kind: practice
tags: [3d-printing, qidi, nozzle, petg-cf, carbon-fiber, wear]
generated: { by: claude/opus-4-8, at: 2026-09-13T20:39:11Z }
verified:
  - { by: human:christopher, at: 2026-09-14T19:48:30Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: 3dput-review
    resource: https://3dput.com/qidi-plus4-review-the-heated-chamber-powerhouse-for-engineering-filaments/
    title: 3DPut Plus 4 review (CF abrasion, nozzle wear)
    last_modified: 2026-09-13
  - id: fixmyprint
    resource: https://www.fixmyprint3d.com/printer-profiles/qidi-plus-4
    title: FixMyPrint Plus 4 profile (clogs on material swaps)
    last_modified: 2026-09-13
not:
  - term: "Run PETG-CF through the stock 0.4mm nozzle indefinitely"
    why: "carbon fiber is abrasive and wears even a hardened-tip bimetal nozzle, degrading dimensional accuracy over time"
    instead: "dedicate a hardened nozzle to CF composites and keep one nozzle per material family"
---

# Practice

The stock 0.4mm bimetal nozzle has a hardened tip and holds up for normal
materials, but carbon/glass-fiber filament is abrasive and will eventually wear
it. For **PETG-CF** a dedicated hardened nozzle is effectively mandatory.

Two operational rules:

1. **One nozzle per material family.** Keep a hardened nozzle for CF composites
   separate from the nozzle used for PLA/PETG/TPU.
2. **Purge hot on swaps.** Users hit clogs switching between TPU, PC-CF, and
   PLA; load/purge at the higher material's temperature when changing.

# Why it matters

A worn nozzle drifts dimensionally, which matters for a fitted part like the
collar. And a mid-print clog from a bad material swap wastes hours. Both are
cheap to avoid with a spare hardened nozzle and a hot purge. See
[[qidi-plus-4-hardware-profile]].
