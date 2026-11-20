---
type: Failure Mode
title: In CadQuery, cut overlapping cutters in separate passes or the solid fragments
description: A single Compound holding two overlapping cutters (a bore and a slot that intersects it) makes the OCC boolean imprint the body into many disconnected per-feature solids. Cut each category in its own sequential .cut() pass.
kind: failure-mode
tags: [cadquery, occ, boolean, stl, mesh, 3d-printing]
generated: { by: claude/opus-4-8, at: 2026-09-14T22:23:46Z }
verified:
  - { by: human:christopher, at: 2026-09-14T22:32:07Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: tray-code
    resource: projects/3d-printing/allen-organizer/src/allen_organizer/tray.py
    title: build_tray cuts channels and slots in separate passes
    last_modified: 2026-09-14
  - id: readme
    resource: projects/3d-printing/allen-organizer/README.md
    title: "Gotcha: cut overlapping cutters in separate passes"
    last_modified: 2026-09-14
not:
  - term: "body.cut(Compound.makeCompound(channels + slots))"
    why: "one compound with a bore and the slot that overlaps it makes the OCC boolean imprint the body into 13 per-station solids; the STL is watertight but fragmented"
    instead: "body.cut(compound(channels)); body = body.cut(compound(slots))  # sequential passes"
---

# Failure Mode

When building a part by subtracting many cutters in CadQuery, do not put two
cutters that *overlap each other* into the same `Compound` for a single
`.cut()`. In the allen-organizer slide tray, each station has a teardrop channel
bore and a short-arm slot that intersects that bore. Cutting both categories in
one combined compound imprinted the body into 13 disconnected per-station solids.
Cutting channels in one pass and slots in the next kept it a single solid.

The tell: `len(result.val().Solids())` was 17 (fragmented), yet the exported
mesh's `is_watertight` was `True`. Watertightness does not catch this;
`trimesh.load(...).split()` returned 17 shells. Verify solidity with
`len(result.val().Solids()) == 1`.

# Why it matters

A fragmented STL made of overlapping shells can look fine and pass a watertight
check, then slice into weak or wrong geometry. The failure is invisible until you
count solids or shells. This cost a long debugging detour: a channel-floor
tangency looked like the cause and a floor gap was added first, but the real
trigger was the combined-compound cut of overlapping cutters.

# Evidence

Bisection with `len(wp.val().Solids())`:
- box then cut channels-compound then cut slots-compound (sequential) → 1 solid
- box then cut a single compound of channels + slots → 14 solids
- full tray via the combined compound → 17 solids; after switching to sequential
  passes → 1 solid, and `trimesh` reported 1 shell (was 17).
