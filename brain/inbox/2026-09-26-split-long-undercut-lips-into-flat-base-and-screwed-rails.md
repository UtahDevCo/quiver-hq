---
type: Observation
title: Split long undercut lips into a flat base and screwed-on flat rails
description: A 4 mm cantilever lip over a 1 mm slot curled when printed flat; a flat pocket base plus flat lip rails printed clean with an exact gap.
kind: pattern
proposed_layer: project
proposed_project: 3d-printing
tags: [fdm, overhang, undercut, print-orientation, coupons]
generated: { by: claude/opus-5.5, at: 2026-09-26T19:33:42Z }
status: draft
sources:
  - id: generator
    resource: projects/3d-printing/collar/src/collar/boa_slot_gauges.py
    title: collar BOA slot coupon generator (docstring history v1 to v5)
    last_modified: 2026-09-26
  - id: handoff
    resource: projects/3d-printing/collar/HANDOFF.md
    title: collar handoff, "Update 2026-09-26" section (v3 and v4 results)
    last_modified: 2026-09-26
not:
  - term: "one-piece part with a 4 mm lip cantilevered over a 1 mm gap, printed flat"
    why: "the first layers over air curl upward, so the lip edge is messy and the gap is not what was modeled"
    instead: "print the pocket as a base open on top (depth = gap) and the lip as a separate flat plate screwed on"
  - term: "stand the part on its side so the lip becomes a vertical wall"
    why: "the lip on the upper side then starts as an unconnected island in each layer"
    instead: "split into flat pieces"
---

# Observation

When a part needs a lip that overhangs a thin slot to capture a flange, a flat one-piece print is fine for short cantilevers: 1.5 mm over a 1.0 mm gap printed clean. At 4 mm over the same gap, the lip curled upward and printed messy (visible blobs and raised edges in the side view).

Splitting the part fixed it. The base is the floor plus walls forming the flange pocket, open on top, with the pocket depth equal to the lip gap. The lip is a separate flat plate, or rails, that sits on the base and is screwed down. Neither piece has an overhang, and the gap is the printed pocket depth, set by layer count, instead of whatever sag leaves.

If a lip must span two regions that other features keep open (here, an open end for the housing and a closed end for laces), the lid comes out as more than one piece. Give each piece its own screws.

# Why it matters

The lip gap is the fit. A curled or sagging cantilever changes it by roughly the flange-clearance margin (0.06 to 0.26 mm here), so a coupon series tuning that gap measures print sag instead of the design.

# Evidence

Collar BOA dial slot coupons, 2026-09-26, PLA+ at 0.2 mm on a Qidi X-Plus 4. v1 (1.5 mm lips, one piece) printed clean. v3 (4.0 mm lips, one piece) worked but the lips curled. v4 (flat base plus two flat rails, M3 screws) printed clean and held the disc with the trailing edge barely lifting.
