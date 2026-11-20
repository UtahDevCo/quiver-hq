---
type: Observation
title: Calibrate Tracefinity from the notebook's dot grid, not the paper outline
description: Tracefinity's paper-corner detection failed on 6 of 8 spiral-notebook photos and returned wrong corners on the other 2; a homography fit to the 5mm dot grid gave 0.8px rms.
kind: workflow
proposed_layer: project
proposed_project: 3d-printing
tags: [tracefinity, gridfinity, photogrammetry, calibration]
generated: { by: claude/opus-5.5, at: 2026-11-05T19:36:56Z }
status: draft
sources:
  - id: tracefinity-corners
    resource: https://github.com/tracefinity/tracefinity/blob/main/docs/gotchas.md
    title: Tracefinity paper corner detection (U2-Net + OpenCV)
  - id: run
    resource: /Users/christopher/Desktop/tool-photos
    title: 8 Pixel photos of razors and a nail clipper on a spiral dot-grid A4 notebook on white marble, 2026-11-05
not:
  - term: "Trust corner_source=detected"
    why: "On the clipper photo the detected corners included the marble and spiral strip; the warped page came out visibly skewed, so the scale was wrong with no warning"
    instead: "Fit the printed dot grid and pass corners of a virtual A4 rectangle projected through that homography, paper_size a4"
---

# Observation

Tracefinity v0.10.1 found no paper corners (`corners=null`) on 6 of 8 photos of a
spiral-bound dot-grid notebook on a white marble counter. On the other 2 it reported
`corner_source: detected`, but the corners were wrong and the flattened page came out skewed.

What worked: detect the printed dots (blackhat morphology, small round blobs on a
bright surround), grow integer lattice indices by BFS from several seeds, snap
predicted nodes to blobs, then RANSAC-fit a homography from grid-mm to image px.
Project a 210x297 mm rectangle centred on the median dot through it and POST
those four points to `/sessions/{id}/corners` with `paper_size: "a4"`. Fits had
261 to 1504 inlier dots at 0.55 to 0.87 px rms. The A4 rectangle's width matched
the page edge to the pixel, which confirms the 5mm pitch and that the notebook is A4.

Script: `grid_corners.py` from the 2026-11-05 tracefinity session (scratchpad;
copy into a project before reuse). Run it inside the container, which has cv2 and scipy.

# Why it matters

A wrong scale cuts pockets that don't fit, and nothing flags it. The dot grid gives
hundreds of reference points across the whole paper plane instead of four edges
that the spiral strip and stacked pages make ambiguous.

# Evidence

Upload responses: `corner_source: none` for 180239, 180243, 180249, 180351,
180359 and 180403; `detected` for 180427 and 180431. The 180427 overlay showed a skewed page.
Cross-checks after grid calibration: safety razor 107.5 mm flat vs 107.9 mm on edge.
Every photo also warned `camera_too_close` (estimated 28 to 30 cm, about 5.5% oversize for a 15 mm tool).
