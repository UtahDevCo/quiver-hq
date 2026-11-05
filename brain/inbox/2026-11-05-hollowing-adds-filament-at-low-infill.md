---
type: Observation
title: Modelled voids add filament at low infill; cut wall loops instead
description: Closed internal voids get their own perimeters, so at 10% infill a hollowed part sliced heavier than the solid one, while dropping wall loops saved a third.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [slicer, filament, cadquery, qidi-studio, fdm]
generated: { by: claude/opus-5.5, at: 2026-11-05T01:31:02Z }
status: draft
sources:
  - id: readme
    resource: projects/battery-bricks/README.md
    title: battery-bricks README, Printing section (slice results)
    last_modified: 2026-11-04
not:
  - term: "hollow the part in CAD to save filament"
    why: "with 10% sparse infill the removed volume was cheap infill, and each new void got wall_loops perimeters plus bridged ceilings; model volume fell 446 to 289 cm³ but the slice rose 238 to 251 g"
    instead: "keep the part solid and lower wall_loops (5 to 3 was 238 to 186 g; 2 was 156 g), then check strength where it matters"
---

# Observation

At low sparse infill (10% gyroid here), modelling closed voids inside a part
does not save filament. The slicer treats each void surface as a wall and
lays `wall_loops` perimeters around it, and bridged ceilings and floor shells
on top of that. The plastic you remove was mostly air already. The wall count
is the lever.

# Why it matters

A model can look a third lighter in CAD and print heavier and slower: the
hollowed brick took 11 h 14 m against 9 h 47 m solid. Without slicing both
versions you would not notice.

# Evidence

AA battery brick, 167.5 x 88.3 x 46.3 mm, QIDI Studio 02.07.02.60, 0.2 mm
layers, 10% gyroid:

| Model | Walls | Filament | Time |
|---|---|---|---|
| solid (446 cm³) | 5 | 238 g | 9 h 47 m |
| voids behind lanes and under bores (289 cm³) | 5 | 251 g | 11 h 14 m |
| same voids | 3 | 206 g | 8 h 55 m |
| solid | 3 | 186 g | 7 h 51 m |
| solid | 2 | 156 g | 6 h 39 m |

Solid beat hollow at every wall count tested.
