---
type: Observation
title: A lip over an open-ended sideways slot prints in mid-air
description: On an upright FDM part, any lip over a horizontal slot that is open at both ends has a lowest edge with nothing below it and no wall to bridge from.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [fdm, overhang, printability, slicer]
generated: { by: claude/opus-5-5, at: 2026-10-09T14:21:44Z }
status: draft
sources:
  - id: evidence
    resource: projects/3d-printing/collar/src/collar/brace_parts.py
    title: _lace_slot docstring and the anchor slot iterations (commits 2b0e113, a8feea9, f1057ec, 6f250f1)
    last_modified: 2026-10-08
not:
  - term: "45 degree faces on both sides of the lip fix it"
    why: "the lip still has a lowest edge where the two faces meet; the island shrank from 24 mm2 to 4 mm2 but did not go away"
    instead: "put no lip on the upper side; slope that face at 45 degrees all the way, and get any trap from an up-facing lip below"
---

# Observation

A trap slot (narrow opening, wider cavity) running sideways on a part printed
upright needs a lip above the opening. If the slot is open at both ends, that
lip's lowest edge has nothing under it and no end wall to bridge from, so its
first layers print on air. 45 degree faces on the lip only shrink the problem.
The upper side must be one continuous 45 degree face with no lip; a flat lip
on the lower side faces up and prints fine.

# Why it matters

QIDI Studio flagged "floating regions" and suggested supports. Tree supports
with "on build plate only" off would have grown into unremovable places (cord
tunnels, the trap itself).

# Evidence

Layer-by-layer island check (trimesh section_multiplane at 0.2 mm, flag
polygons that miss the layer below): 24.4 mm2 island with a flat-bottomed lip,
4.3 mm2 with 45 degree lip faces, none with a lipless 45 degree upper face.
Slicing exactly through a corner gave false islands, so the check runs at two
or three slice offsets.
