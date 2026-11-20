---
type: Observation
title: Gridfinity base foot profile spec for modeling drawer-compatible bins
description: Grid 42mm, cell footprint 41.5mm, foot chamfer stack 0.8/1.8/2.15mm, corner radii 3.75/2.95mm. Baseplates mate the foot perimeter, so features on a perpendicular face or recessed in a cell center keep compatibility.
kind: module
proposed_layer: project
proposed_project: 3d-printing
tags: [gridfinity, cad, cadquery, drawer, bin, reference]
generated: { by: claude/opus-4-8, at: 2026-09-15T17:10:55Z }
status: draft
sources:
  - id: gridfinity-rebuilt
    resource: https://github.com/kennetek/gridfinity-rebuilt-openscad
    title: gridfinity-rebuilt standard.scad constants
    last_modified: 2026-09-15
  - id: spec
    resource: https://gridfinity.xyz/specification/
    title: Gridfinity specification
    last_modified: 2026-09-15
  - id: code
    resource: projects/3d-printing/allen-organizer/src/allen_organizer/gridfinity.py
    title: CadQuery foot generator built from these numbers
    last_modified: 2026-09-15
---

# Observation

To model a Gridfinity-drawer-compatible bin, the only thing that must be exact is
the base foot profile (it mates the baseplate socket). Dimensions in mm:

- **Grid pitch:** 42 × 42.
- **Foot top (per cell):** 41.5 × 41.5 (0.5 total clearance in the cell).
- **Foot cross-section, bottom → top:** 0.8 chamfer (45°) → 1.8 straight → 2.15
  taper (45°) up to full width. Foot height ~4.75.
- **Corner radius:** top 3.75, bottom 2.95.
- **Bin outer size:** grid·n − 0.5.
- **Height unit:** 7 (bins need not be a multiple; height above the foot is free).
- **Optional magnet/screw holes:** 6.5 dia magnet / 3 dia screw, one per cell
  corner, 8 in from each cell edge (26 spacing).

Baseplates grip the foot's **perimeter chamfer**, not the cell center. So you can
recess features into a cell center, or put them on a face perpendicular to the
foot, without breaking baseplate mating. In the allen-organizer bin, Elfa
dovetail sockets went on the back (−Y) face while the foot stayed on the bottom.

# Why it matters

Get the chamfer stack wrong and the bin won't seat in any baseplate — the whole
point of Gridfinity is cross-vendor interchangeability. Knowing baseplates mate
the perimeter (not the center) is what makes it safe to add non-Gridfinity
mounts to the same part.

# Evidence

Built `gridfinity.py` from these constants: `base(nx, ny)` lofts three rounded-
rect sections per cell (top taper, straight, bottom chamfer) and arrays them at
42mm pitch. A 5×2 base + body slab exported as one watertight solid, footprint
209.5 × 83.5, foot tops at z=0.
