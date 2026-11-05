---
type: Observation
title: Audit new G-code against the last completed print before starting it
description: The QIDI Studio CLI emits G2/G3 arcs and a BOX_TEMP_SET line that Chris's Plus 4 does not define; diffing command words against a known-good print caught both, while /printer/gcode/help gave false alarms.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [qidi-plus-4, klipper, gcode, moonraker, qidi-studio]
generated: { by: claude/opus-5.5, at: 2026-11-04T23:22:49Z }
status: draft
sources:
  - id: coupon-gcode
    resource: projects/battery-bricks/build/fit-coupon.gcode
    title: Audited CLI-sliced coupon (enable_arc_fitting = 0, BOX_TEMP_SET stripped)
    last_modified: 2026-11-04
  - id: printer-macros
    resource: http://192.168.86.64/server/files/config/gcode_macro.cfg
    title: Printer macros call DISABLE_BOX_HEATER (lines 471, 514); no BOX_TEMP_SET anywhere
    last_modified: 2026-11-04
not:
  - term: "check every command word against /printer/gcode/help"
    why: "Klipper's help lists only commands registered with help text; DISABLE_BOX_HEATER and UNLOAD_FILAMENT are missing from it yet ran fine in the last completed print"
    instead: "collect the command words of the last print that /server/history/list shows as completed, fetch its file from /server/files/gcodes/<name>, and require the new file to add none"
  - term: "the system 0.20mm Standard @XPlus4 process as-is"
    why: "it enables arc fitting; the printer has no [gcode_arcs], so the first G2 would abort the print partway through"
    instead: "set enable_arc_fitting = 0 (matches what the GUI-sliced prints use)"
---

# Observation

Before uploading CLI-sliced G-code, diff its set of command words (first
token of each non-comment line) against the most recent print that
`/server/history/list` reports as `completed`. Any new word is a stop.

On the Plus 4 this caught two problems:

- `G2`/`G3` from arc fitting, which the system process preset enables. The
  printer has no `[gcode_arcs]`. Fix: `enable_arc_fitting = 0`.
- `BOX_TEMP_SET VT0=0`, injected by the CLI right before `PRINT_START` and
  defined nowhere in the printer config. Fix: delete that line after slicing.

# Why it matters

Klipper aborts a print on an unknown command. Arcs first appear partway
into the print, after heat-up and the first layers, so the failure costs real
time and filament and looks like a printer fault.

# Evidence

Fit coupon, 2026-11-04. First audit against `/printer/gcode/help` flagged
`BOX_TEMP_SET`, `DISABLE_BOX_HEATER` and `UNLOAD_FILAMENT`. Two of those were
false alarms: `DISABLE_BOX_HEATER` and `UNLOAD_FILAMENT` are in the end
G-code of `B5_Key_test_xy-0.1.gcode`, which completed on 2026-11-01. The diff
against that file reported `['BOX_TEMP_SET', 'G2']`. After the two fixes it
reported none, and the print started cleanly.
