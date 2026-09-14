---
type: Module
title: Plus 4 per-material slicer starting settings (PLA+/PETG/PETG-CF/TPU)
description: Starting nozzle/bed/chamber/speed ranges for the four filaments Chris runs. Community starting points; QIDI Studio's built-in presets are the authoritative source.
kind: module
tags: [3d-printing, qidi, slicer, settings, pla, petg, petg-cf, tpu, reference]
generated: { by: claude/opus-4-8, at: 2026-09-13T20:39:11Z }
verified:
  - { by: human:christopher, at: 2026-09-14T19:48:30Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: qidi-review
    resource: https://qidi3d.com/blogs/news/qidi-plus-4-3d-printer-review
    title: QIDI Plus 4 review
    last_modified: 2026-09-13
  - id: tpu-wiki
    resource: https://wiki.qidi3d.com/en/filament/tpu-printing-guide
    title: QIDI TPU printing guide
    last_modified: 2026-09-13
  - id: orca-profiles
    resource: https://github.com/Xorlent/Orcaslicer-Qidi-Plus-4
    title: Community OrcaSlicer profiles for the Plus 4
    last_modified: 2026-09-13
  - id: plus4-wiki
    resource: https://github.com/qidi-community/Plus4-Wiki
    title: Community Plus4-Wiki
    last_modified: 2026-09-13
---

# Module

Starting-point slicer ranges for the four filaments Chris runs on the Plus 4.

| Material | Nozzle °C | Bed °C | Chamber | Speed |
|---|---|---|---|---|
| **PLA / PLA+** | 190–220 | 50–60 | **Off, door open, top off** | up to ~300 mm/s |
| **PETG** | 230–250 | 80–90 | Off / closed OK | ~300 mm/s; slow walls ~35–40%, flow ~0.96 |
| **PETG-CF** | 230–260 | 70–80 | Off / low | slow; **hardened nozzle required** |
| **TPU (95A)** | 220–240 | 35–45 | Off | slow; 0.4mm nozzle, low max volumetric speed |

# Why it matters

These get a print started without a full tuning cycle. The chamber column
encodes the [[plus-4-chamber-heat-off-for-pla-and-tpu]] rule; PETG-CF's
"hardened nozzle" is [[cf-filament-needs-dedicated-hardened-nozzle]].

# Caveats

**QIDI Studio's built-in per-material presets are authoritative** — pick the
filament in the slicer and it auto-loads them. The numbers above are community
ranges cross-checked across reviews and the Orca profile repo, NOT pulled from
QIDI's own spec sheet (the QIDI wiki filament tables are JS-rendered and did not
extract). "PLA+" is a marketing umbrella; if a specific spool ships a datasheet,
prefer it over this table.
