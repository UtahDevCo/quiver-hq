---
type: Module
title: Elfa Utility Board clip (thing:4060473) mounts parts via a half-dovetail bar
description: The reusable spring-clip locks into the board; parts carry a female half-dovetail socket that slides vertically onto the clip's outward bar. Socket is 3.3mm mouth to 6.8mm base over 6mm depth, one vertical face and one sloped. Board slot pitch measured 32.5mm.
kind: module
tags: [elfa, pegboard, mount, dovetail, 3d-printing, reference]
generated: { by: claude/opus-4-8, at: 2026-09-14T22:23:46Z }
verified:
  - { by: human:christopher, at: 2026-09-14T22:32:07Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: thingiverse
    resource: https://www.thingiverse.com/thing:4060473
    title: Modular Tool Racks for Elfa Utility Board by RockyMtnMark
    last_modified: 2026-09-14
  - id: saddle-code
    resource: projects/3d-printing/allen-organizer/src/allen_organizer/clip_saddle.py
    title: Socket profile cloned from the vendor rack leg
    last_modified: 2026-09-14
  - id: pitch
    resource: projects/3d-printing/allen-organizer/config/inventory.json
    title: mount.board_pitch_mm = 32.5 (Chris measured 32.44 with a micrometer)
    last_modified: 2026-09-14
---

# Module

To hang a printed part on Chris's Elfa Utility Board, reuse the vendor system
from thing:4060473 rather than modeling a board interface: print
`ElfaModuleClip.stl` (the spring-clip that locks into the board slot) and give
your part a female socket that slides vertically down onto the clip's
outward-facing bar. The clip's bottom stop holds the part up; it lifts off the
top.

The bar/socket is a **half-dovetail** (one vertical face, one sloped hypotenuse),
reverse-engineered from the vendor rack leg (section at Z=8):
- socket base (deep, part side): ~6.79 mm wide
- socket mouth (board side): ~3.32 mm wide
- depth: 6 mm; the undercut traps the bar so it can only slide vertically

Clone the socket profile verbatim from the vendor leg and it mates by
construction. **Board slot pitch: 32.5 mm** (measured 32.44). Space multiple
sockets a whole multiple of that pitch so each lands on a clip in an adjacent
slot column.

**Clip orientation is directional: spring end DOWN, hook end UP.** The spring
locks into the board slot and the hook catches over the top for gravity load.
Orient the part's socket to slide down onto a clip mounted that way. The bar
cross-section is constant along its length, so up/down does not change the
dovetail handedness, but the clip's bottom stop (spring end) is what the part
rests on, so it must be at the bottom.

**Clearance: use 0.35 mm** (PLA, QIDI Plus 4, 0.4 nozzle). Tested on printed
saddles against a printed clip: 0.25 mm was a hammer-in fit, 0.35 mm slides on
and off freely by hand. Freely is correct here — the dovetail undercut still
traps the part against a straight forward pull-off at 0.35 (it only releases by
sliding back up the bar), so retention comes from the undercut plus gravity plus
the clip's bottom stop, not from friction. Do not chase a tight friction fit; for
a gravity-hung part an easy vertical slide is the target and makes a large
multi-socket part mountable by hand. The printer eats ~0.25-0.3 mm of nominal
clearance, so the sliding gap at 0.35 is small.

# Why it matters

Board-mounted prints are a recurring need (Chris runs a QIDI Plus 4 and has an
Elfa board). Cloning the vendor socket and reusing their clip removes all fit
risk on the board side; you only tune the printed slide tolerance. Getting the
pitch wrong means two clips won't both align with two sockets.

# Evidence

Sectioning the vendor meshes with trimesh: the clip's outward bar is a right
trapezoid ~6x6 mm (vertical face + diagonal); the rack leg has a matching
triangular socket with a 3.32 mm mouth over a 6.79 mm base. A cloned socket
(`clip_saddle.py`) built as an `elfa-saddle-fit-test.stl` for a one-clip slide
check before committing to a full tray.

# Caveats

Confirmed on printed runs (2026-09-14, PLA): the vendor clip snaps into the Elfa
board and the cloned saddle mates its bar. 0.25 mm hammered on; 0.35 mm slides
freely yet still traps against a forward pull-off. 0.35 mm is the chosen
clearance. The clip's spring-down/hook-up orientation was learned here, not from
the vendor docs.
