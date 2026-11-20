---
type: Observation
title: Tracefinity placed tools are re-derived from the library on every GET
description: Bin auto-placement overlaps tools; when laying out via the API, set rotation AND points consistently, because sync_placed_tools rebuilds points from library + rotation + placed centroid.
kind: module
proposed_layer: project
proposed_project: 3d-printing
tags: [tracefinity, gridfinity, api]
generated: { by: claude/opus-5.5, at: 2026-11-05T19:36:56Z }
status: draft
sources:
  - id: sync
    resource: https://github.com/tracefinity/tracefinity/blob/main/backend/app/services/bin_service.py
    title: sync_placed_tools rotates library points about their centroid and moves them to the placed centroid
not:
  - term: "rotate the placed points directly and leave rotation=0"
    why: "the next GET /bins/{id} re-syncs from the library and un-rotates the tool in place"
    instead: "set placed_tool.rotation, and write points = library points rotated by it about the library centroid, translated to the target centroid"
---

# Observation

`POST /api/bins` with three `tool_ids` auto-sized to 3x4 and placed the safety razor
and nail clipper overlapping (bboxes from x 9 and 14, y 70 and 73).
Lay bins out yourself. `GET /bins/{id}` re-derives each placed tool's points: library
points rotated by `rotation` degrees about the library centroid, then moved to the
current placed centroid. Only the centroid and `rotation` survive. `depth_override`
is per placed tool and is the only depth control: one flat pocket floor per tool.

# Why it matters

A layout written any other way moves on the next load, and the preview and STL drift from what you planned.

# Evidence

Layout script `layout.py` (2026-11-05 session scratchpad) followed this rule. The
generated STL's pocket floors measured exactly the requested depths (30, 20, 14 and 15 mm
below the 42 mm floor face).
