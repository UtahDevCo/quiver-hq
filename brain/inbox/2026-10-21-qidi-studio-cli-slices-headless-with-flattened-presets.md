---
type: Observation
title: QIDI Studio slices headless from its own binary with flattened presets
description: QIDIStudio.app ships a Bambu-style CLI that arranges, clones, slices and exports 3MF plus G-code; presets must be flattened through their inherits chain, bed type set explicitly, and PNG export fails headless.
kind: module
proposed_layer: project
proposed_project: 3d-printing
tags: [3d-printing, qidi-studio, slicer, cli, automation]
generated: { by: claude/opus-5.5, at: 2026-10-21T18:05:00Z }
status: draft
sources:
  - id: cli-help
    resource: /Applications/QIDIStudio.app/Contents/MacOS/QIDIStudio --help
    title: QIDI Studio 02.07.02.60 CLI usage
    last_modified: 2026-10-21
  - id: presets
    resource: ~/Library/Application Support/QIDIStudio/user/default/process/
    title: Chris's QIDI Studio process presets (PLA plus, PETG, PETG-CF, ...)
    last_modified: 2026-10-21
not:
  - term: "--export-png 0 in a headless run"
    why: "slicing succeeds and writes plate_1.gcode, then the run exits 254 with 'Invalid parameters to the slicer' because plate rendering needs a GL context"
    instead: "omit --export-png; read object placement from result.json sliced_plates[].objects[].bbox"
  - term: "--load-settings pointing at a user or system preset JSON as-is"
    why: "presets are deltas over an inherits chain (user 'PLA plus' -> '0.20mm Standard @XPlus4' -> 'fdm_process_common'); internal names differ from file names ('X-Plus 4 0.4 nozzle' lives in 'Qidi X-Plus 4 0.4 nozzle.json')"
    instead: "index system/**/{machine,process,filament}/*.json and user/default/* by their 'name' field, merge parent-first, drop 'inherits'"
---

# Observation

`/Applications/QIDIStudio.app/Contents/MacOS/QIDIStudio` (v02.07.02.60) is a working slicer CLI:

```text
QIDIStudio --load-settings "machine.json;process.json" --load-filaments "filament.json" \
  --clone-objects "8,4" --arrange 1 --allow-rotations --orient 0 \
  --slice 0 --export-3mf out.3mf --outputdir DIR a.stl b.stl
```

`--clone-objects` takes a copy count per input file, in order. Output: `out.3mf` (opens in the
GUI, G-code embedded), `plate_1.gcode`, and `result.json` with `return_code`, print time
(`main_predication`, seconds), grams, and each object's placed bbox.

Settings that must be set explicitly because the defaults are wrong for Chris's Plus 4:
`curr_bed_type = "Textured PEI Plate"` (default Cool Plate gives `PRINT_START BED=45` for PLA
instead of 60).

# Why it matters

Removes the GUI from slicing. The arrange step also replaces paper plate-fit estimates: VAULT
plate B1 (8 runner guides + 4 rail pairs) arranged onto one 305 mm plate with every bbox inside
the bed.

# Evidence

2026-10-21, plate B1: user "PLA plus" process (100% infill) sliced to 11.0 h / 340 g; stock
`0.20mm Standard @XPlus4` (15% grid, 2 walls) with textured PEI sliced to 6.5 h / 191 g,
`PRINT_START BED=60 HOTEND=220`. The printer's Moonraker host (192.168.86.64, configured as
`host_type: octoprint` in `user/default/physical_printer/Qidi 4.json`) did not answer ping at
the time, so upload was not tested.
