---
type: Practice
title: Dry TPU and PETG-CF before printing and feed them straight from the dryer
description: TPU and PETG-CF are the most hygroscopic filaments Chris runs and re-absorb water fast; dry them, print from the dryer as a heated dry-box, and store sealed with desiccant. Wet symptoms are popping, stringing, and weak parts.
kind: practice
tags: [3d-printing, drying, moisture, tpu, petg-cf, storage, sunlu]
generated: { by: claude/opus-4-8, at: 2026-09-13T20:39:11Z }
verified:
  - { by: human:christopher, at: 2026-09-14T19:48:30Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: sigma-manual
    resource: https://sigmafilament.com/sunlu-filament-dryer-manual-settings/
    title: SigmaFilament SUNLU guide (hygroscopic ranking, wet symptoms, storage)
    last_modified: 2026-09-13
  - id: sunlu-comparison
    resource: https://store.sunlu.com/blogs/3d-printing-guide/sunlu-s2-vs-s4-vs-e2-filament-dryer-comparison-2026
    title: SUNLU comparison (PTFE feed-through for printing from the dryer)
    last_modified: 2026-09-13
not:
  - term: "Leave TPU or PETG-CF on an open shelf between prints and load straight from the spool"
    why: "both re-absorb moisture within hours; printing wet filament causes popping, stringing, rough surfaces, and brittle/weak parts"
    instead: "dry it, then either print immediately from the dryer's PTFE feed-through or store sealed with fresh desiccant"
---

# Practice

Hygroscopic ranking, most to least: nylon > **TPU** > **PETG / PETG-CF** > ABS/ASA
> PLA. Of Chris's four, **TPU and PETG-CF need drying most urgently** and
re-wet fastest; PETG-CF is often wet out of the box.

Three rules:

1. **Dry before printing** on the schedule in
   [[sunlu-dryer-schedule-per-material]].
2. **Feed from the dryer while printing** for TPU and PETG-CF. All SUNLU models
   have a PTFE tube feed-through, so the dryer doubles as a heated dry-box for
   long prints. PLA+ tolerates ambient print time fine and doesn't need this.
3. **Store sealed with fresh desiccant** (airtight box or vacuum bag). Don't
   leave the moisture-sensitive spools out between prints.

**Wet-filament symptoms:** popping/crackling/hissing at the nozzle (steam),
heavy stringing and oozing, rough/fuzzy surface, poor layer adhesion, brittle
parts, dimensional inaccuracy.

# Why it matters

For the collar, TPU is the fit-critical material: wet TPU prints weak and rough,
which corrupts both fit tests and any load-bearing part. Drying is the cheapest
lever on TPU/PETG-CF quality, and the symptoms above are usually misread as a
temperature or speed problem.
