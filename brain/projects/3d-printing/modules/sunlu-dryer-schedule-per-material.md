---
type: Module
title: SUNLU dryer schedule for PLA+/PETG/PETG-CF/TPU
description: Drying temp/time per material. SUNLU S2/S4 cap at 70°C, which covers all four; E2's 110°C is only for high-temp engineering filaments.
kind: module
tags: [3d-printing, sunlu, dryer, drying, pla, petg, petg-cf, tpu, reference]
generated: { by: claude/opus-4-8, at: 2026-09-13T20:39:11Z }
verified:
  - { by: human:christopher, at: 2026-09-14T19:48:30Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: sunlu-comparison
    resource: https://store.sunlu.com/blogs/3d-printing-guide/sunlu-s2-vs-s4-vs-e2-filament-dryer-comparison-2026
    title: SUNLU S2 vs S4 vs E2 comparison (max temps, capacities)
    last_modified: 2026-09-13
  - id: sigma-manual
    resource: https://sigmafilament.com/sunlu-filament-dryer-manual-settings/
    title: SigmaFilament SUNLU manual settings (per-material temp/time, wet symptoms)
    last_modified: 2026-09-13
  - id: sunlu-s2
    resource: https://store.sunlu.com/products/new-version-sunlu-filadryer-s2
    title: SUNLU FilaDryer S2 product page (default 50°C/6h PLA preset)
    last_modified: 2026-09-13
---

# Module

Drying schedule for the four filaments Chris runs.

| Material | Temp | Time |
|---|---|---|
| PLA / PLA+ | 45–50 °C | 4–8 h (PLA+ toward 6–8) |
| PETG | 65–70 °C | 6–8 h |
| PETG-CF | 70 °C | 8+ h |
| TPU | 45–55 °C ("low and slow") | 8–12+ h |

**Model temp caps:** S2 and S4 top out at **70 °C**; E2 reaches **110 °C**.
70 °C covers all four of these materials, so S2/S4 is enough — the E2's 110 °C
only matters for nylon-CF / PC / PPS.

**Keep PLA ≤ 50 °C:** its glass transition is ~55–60 °C, so 70 °C would soften
and deform the spool.

# Why it matters

Wrong temp either fails to drive out moisture (too low) or slumps the spool (PLA
too hot). Which materials most need this, plus wet-filament symptoms and
feed-from-dryer, are in [[dry-hygroscopic-filament-and-feed-from-dryer]].

# Caveats

The per-material numbers are a community-guide consensus cross-checked against
SUNLU's own comparison page and the S2's default PLA preset (50 °C / 6 h). Some
makers spec PETG-CF at 65 °C; prefer a specific spool's datasheet if it has one.
