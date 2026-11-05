---
type: Observation
title: Slice for the Plus 4 headless with the QIDI Studio CLI
description: QIDIStudio --slice works from the shell if presets are resolved by their JSON name, keep a system parent in inherits, and get an absolute --outputdir and an explicit bed type.
kind: workflow
proposed_layer: project
proposed_project: 3d-printing
tags: [qidi-plus-4, qidi-studio, slicer, cli, moonraker]
generated: { by: claude/opus-5.5, at: 2026-11-04T23:22:49Z }
status: draft
sources:
  - id: coupon-gcode
    resource: projects/battery-bricks/build/fit-coupon.gcode
    title: CLI-sliced fit coupon that printed on the Plus 4 (header holds the full resolved config)
    last_modified: 2026-11-04
  - id: system-profiles
    resource: /Applications/QIDIStudio.app/Contents/Resources/profiles/X 4 Series
    title: QIDI Studio 02.07.02.60 system presets for the X-Plus 4
    last_modified: 2026-11-04
not:
  - term: "inherits resolved by filename, e.g. 'Qidi X-Plus 4 0.4 nozzle.json'"
    why: "the inherits chain names presets by their JSON name field; the machine file 'Qidi X-Plus 4 0.4 nozzle.json' is named 'X-Plus 4 0.4 nozzle'"
    instead: "index every profile JSON by (type, name) and walk inherits through that index"
  - term: "fully resolved presets with inherits removed"
    why: "the CLI then rejects the process: 'The selected printer is not compatible with the process preset' (return_code -17), even with compatible_printers cleared"
    instead: "keep the resolved values but set inherits to the system parent name ('X-Plus 4 0.4 nozzle', '0.20mm Standard @XPlus4', 'Generic PLA @Qidi X-Plus 4 0.4 nozzle')"
  - term: "--outputdir out (relative)"
    why: "exit 0 and the log says 'Project exported to out/coupon.3mf', but nothing appears in ./out"
    instead: "pass an absolute --outputdir and absolute --load-settings paths"
---

# Observation

QIDI Studio (a Bambu Studio fork) slices from the shell:

```sh
/Applications/QIDIStudio.app/Contents/MacOS/QIDIStudio \
  --curr-bed-type "Textured PEI Plate" --slice 0 \
  --load-settings "$D/machine.json;$D/process.json" --load-filaments "$D/filament.json" \
  --outputdir "$D/out" --export-3mf part.3mf part.stl
```

`$D/out/plate_1.gcode` is plain G-code you can POST to Moonraker
(`/server/files/upload` with `print=true`). To build the three JSONs, index
every profile under `Contents/Resources/profiles/**` by `(type, name)`, walk
`inherits` to merge the chain, apply your overrides, then set `inherits` back
to the system parent's name. Pass `--curr-bed-type` explicitly. The default
is Cool Plate, which sets the bed to 45 °C instead of the 60 °C Chris uses on
the textured PEI plate.

# Why it matters

Lets an agent slice and start a print end to end without the GUI. Each of the
traps in `not:` cost a failed or silent slice. The bed-type default produces
a print that looks right but runs a cold bed.

# Evidence

Battery-bricks fit coupon, 2026-11-04: four failed attempts (KeyError on
filename-based inherits, -17 compatibility error twice, empty relative
outputdir) before the working invocation above. The result was 37.8 g and
1 h 31 m. See `fit-coupon.gcode` header: `curr_bed_type = Textured PEI Plate`,
`textured_plate_temp = 60`.
