---
type: Practice
title: Magigoo Original covers all four filaments; for PETG it's a release barrier that stops PEI tear-out
description: The blue-cap Magigoo Original works for PLA/PETG/PETG-CF/TPU. Its grip-hot/release-cool film also protects the textured PEI from PETG bonding too hard and ripping chunks out of the plate. No specialty variant needed for these materials.
kind: practice
tags: [3d-printing, adhesion, magigoo, petg, pei, bed, release-agent]
generated: { by: claude/opus-4-8, at: 2026-09-13T20:39:11Z }
verified:
  - { by: human:christopher, at: 2026-09-14T19:48:30Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: magigoo-instructions
    resource: https://magigoo.com/magigoo-original-instructions/
    title: Magigoo Original instructions (materials, application, bed temps)
    last_modified: 2026-09-13
  - id: petg-pei-damage
    resource: https://www.sovol3d.com/blogs/news/bed-adhesion-tips-for-petg-abs-easy-fixes-common-problems
    title: PETG over-adhesion and PEI tear-out
    last_modified: 2026-09-13
  - id: filament2print-petgcf
    resource: https://filament2print.com/en/pet-petg-cpe/904-petg-carbon-fiber.html
    title: PETG-CF guide (recommends Magigoo for easier release at 65–75°C bed)
    last_modified: 2026-09-13
not:
  - term: "Print PETG directly on bare textured PEI above ~80°C with no barrier"
    why: "PETG can bond to bare PEI harder than the PEI film bonds to its steel sheet, tearing chunks out of the plate on removal"
    instead: "lay a thin Magigoo Original film as a barrier/release agent, or keep the bed ≤80°C on bare PEI"
  - term: "Buy a specialty Magigoo (PA/PC) for PETG-CF"
    why: "the PA and PC variants are for nylon and polycarbonate; PETG-CF adheres like PETG"
    instead: "use Magigoo Original for all of PLA+/PETG/PETG-CF/TPU"
---

# Practice

**Magigoo Original (blue cap)** officially supports PLA, ABS, PETG, TPU, ASA,
HIPS — so it covers all four filaments Chris runs, PETG-CF included (it adheres
like PETG). No PA/PC specialty variant is needed for these materials.

**Application:** press the tip on a clean bed to open the valve, spread a thin
even layer over the print area, best on a cold bed (works hot too), on
glass/PEI/flex plates. Reapply per print (a 50ml tube lasts 100+ prints); second
coat for warp-prone parts; dab water to release a part that stuck too hard.
Magigoo's own bed temps: PLA 40–60°C, PETG 60–90°C, TPU 40–80°C.

**The PETG case is the important one.** Magigoo grips hot and releases as the
bed cools, and the film sits between filament and plate as a **barrier**. On
bare textured PEI above ~80°C, PETG can bond harder than the PEI film bonds to
its steel sheet and tear chunks out of the plate. Magigoo (or a glue-stick
layer) prevents that direct PETG-to-PEI weld. So for PETG/PETG-CF, Magigoo is
used as protection/release, not because PETG needs help sticking.

**Per-material adhesion rule:**
- **PLA+** — needs help sticking (low bed temp, weak tack). Magigoo for reliable
  first layers + clean cold release. Bed ~40–60°C.
- **PETG / PETG-CF** — needs a release/barrier, not more grip. Magigoo Original,
  bed ~65–90°C, don't over-squish the first layer, let the bed cool fully before
  removal.
- **TPU** — moderate grip; the dominant quality lever is dry filament, not
  adhesion (see [[dry-hygroscopic-filament-and-feed-from-dryer]]).
  Magigoo works, bed 40–80°C.

# Why it matters

The Plus 4 ships a dual-sided textured PEI plate ([[qidi-plus-4-hardware-profile]]);
replacing a PEI sheet that PETG tore up is the avoidable cost here. Using Magigoo
as a barrier protects the plate and gives predictable cold release across all
four materials.
