# Collar project handoff — 2026-09-16

## Executive status

The subject-specific TPU inner sleeve has been designed from Melissa's neck scan, printed, and physically tried. The user reports that it **looks and fits great**. The current sleeve geometry, restrained flares, and smoothed central brace interface should be treated as the validated baseline.

The next subsystem is the external tightening brace. An initial tall, overlapping segmented brace was modeled around a 19.19 mm snowboard-style ladder strap. That physical buckle does not operate reliably at the collar's tight curvature because its lever cannot travel low enough to engage the teeth. That path is parked.

The active direction is a spare **BOA S2-S** dial and lace. The immediate experiment is a four-variation, numbered PLA seat-gauge plate that tests only the measured underside diameters and axial seating. The gauges deliberately have no snap-retention features. The user has not yet reported the print/fit result.

## Physical validation and decisions

- Source anatomy: `stl/melissa-neck-scan.stl`.
- The printed inner sleeve was made in generic TPU 95A on a Qidi X-Plus 4.
- Successful sleeve orientation/settings: upright on the lower flare, 0.20 mm layers, 5 mm brim, no supports. The slicer was set to 100% infill, although this thin shell is principally wall geometry.
- The initial flares were too dramatic. They were reduced to follow the subject more closely; the user approved the revised flares.
- The middle exterior was made less lumpy with a low-frequency, containing Fourier envelope so an external brace can bear against it smoothly.
- The registered fit scene was generated directly from the scan and sleeve; Blender is not required for the current parametric workflow.
- No tensioned human trial of the outer brace or BOA system has occurred.

## Current source and generated artifacts

Primary source files:

- `src/collar/scan.py` — scan loading, scaling, section extraction.
- `src/collar/fit_gauges.py` — early section-fit gauges.
- `src/collar/full_sleeve.py` — current full TPU sleeve.
- `src/collar/fit_scene.py` — registered scan/sleeve visualization assets.
- `src/collar/outer_brace.py` — segmented brace concept for the now-parked ladder-strap hardware.
- `src/collar/boa_seat_gauges.py` — active BOA S2-S fit-coupon experiment.
- `config/melissa.json` — scan, sleeve, fit-scene, and brace parameters.
- `BOA_SEAT_GAUGES.md` — printing and evaluation instructions for the current experiment.

Important generated outputs:

- `build/full-sleeve/melissa-inner-sleeve-prototype.stl`
- `build/full-sleeve/melissa-inner-sleeve-prototype.step`
- `build/full-sleeve/melissa-inner-sleeve-prototype.3mf`
- `build/fit-scene/melissa-fit-scene.glb`
- `build/fit-scene/melissa-inner-sleeve-scan-coordinates.stl`
- `build/fit-scene/melissa-neck-chin-shoulders-proxy.stl`
- `build/outer-brace/` — eight segments, concept assemblies, and ladder-strap envelopes; reference work only.
- `build/boa-seat-gauges/boa-s2s-seat-gauges-1-to-4-plate.stl` — next recommended print.
- `build/boa-seat-gauges/boa-s2s-seat-gauge-{1,2,3,4}.stl` — individual variants.
- `build/boa-seat-gauges/manifest.json` — exact gauge dimensions.

The generated build directory appears to be ignored by Git; regenerate artifacts rather than assuming they will travel with a commit.

## Parametric sleeve baseline

Key values in `config/melissa.json`:

- Scan units: metres; imported at 1000x to millimetres.
- Axes: X left/right, Y vertical, Z posterior/anterior; anterior is +Z.
- Expected neck centre near X = -20 mm, Z = -345 mm.
- Sleeve construction: controlled hourglass.
- Reference Y level: -47.5 mm.
- Core height: 38 mm.
- Upper and lower flare height: 18 mm.
- Flare outset: 8 mm, over 8 steps.
- Skin clearance: 2 mm.
- Wall thickness: 2.4 mm.
- Rear opening: 24 mm.
- Outer brace interface: 192-sample, six-harmonic containing Fourier envelope.
- Alignment sections: Y = -60, -55, -50, -47.5, -45, -42.5 mm.
- Rear-overlap correction is disabled. An observed 25.4 mm value remains recorded for reference.

Avoid changing these values until there is a specific fit issue; the physical sleeve is the best validated part of the project.

## Parked ladder-strap brace direction

The brace concept has eight interlocking/overlapping segments, approximately 36 mm tall (about 1.42 inches), with radial half-laps intended to conceal the strap and keep the exterior continuous. The user liked this appearance.

Measured physical hardware:

- Ladder strap width: 19.19 mm.
- Strap thickness: 3.9 mm.
- Buckle width: 30.4 mm.
- Buckle length: 65.58 mm.
- Buckle height/depth envelope: 30.36 mm.
- Ten-tooth span: 38.6 mm, measured from the first tooth high point to the tenth tooth low point.
- Strap length: approximately 18 inches; it could be trimmed and teeth removed to create a hard tightening limit.

Reason parked: when wrapped to this neck circumference, the buckle lever cannot reach low enough to grab the teeth. Do not resume this hardware unchanged. The source and photos remain useful if a remote/tangent buckle mount is later explored.

Relevant photos are `images/ratchet-*.jpg`.

## Active BOA S2-S direction

The spare dial is positively identified by its supplied leaflet as a left/right-specific BOA **S2-S** system. The shoe's receiver is not a normal user-replaceable repair component: the official S2-S repair procedure replaces the dial/reel and lace while retaining the receiver sewn into the shoe.

A public receiver STL/STEP matching this unit was not found. A University of Idaho thesis used S2-S dials in printed exoskeleton cuffs and reported that reproducing the snap geometry reliably was difficult; that project moved to a bolt-mounted standard S2. This supports the current strategy: characterize the fit with tiny coupons, then make a replaceable receiver cartridge rather than building the mount permanently into the collar.

The scan at `stl/boa-buckle.stl` contains the shoe, table/wall capture, and noisy black-plastic geometry. It is not trimmed and is not presently the preferred dimensional source.

### Measurements extracted from `images/boa/`

High-confidence/direct readings used by the gauge model:

- Cartridge narrow axis: 26.32 mm.
- Total cartridge height: 11.65–11.76 mm.
- Underside stepped diameters: 18.73 mm and 20.45 mm.
- Axial step: 1.15 mm.
- Combined axial step: 2.21 mm.
- Original shoe receiver outside diameter: 30.24 mm.
- Base flange thickness: 2.52 mm.

Readings that should be rechecked before final receiver design:

- Cartridge long axis: recorded as approximately 27.95 mm; the photo/display interpretation is less certain.
- Opposing internal feature spacing: approximately 9.80 mm.
- Another underside step: approximately 1.78 mm.
- Mounted receiver height: approximately 11.75 mm.
- Mounted outside envelope: approximately 31.99 mm.
- Small receiver opening: approximately 8.27 mm.
- Exact snap-window width, tab angular positions, undercut depth, and functional retention/release clearances remain unknown.

Most useful measurement photos:

- `images/boa/PXL_20260820_161738279.jpg` — 26.32 mm.
- `images/boa/PXL_20260820_161753505.jpg` — 9.80 mm.
- `images/boa/PXL_20260820_161927162.jpg` — 11.65 mm.
- `images/boa/PXL_20260820_163149876.jpg` — 30.24 mm.
- `images/boa/PXL_20260820_165823648.jpg` — 18.73 mm.
- `images/boa/PXL_20260820_165837634.jpg` — 20.45 mm.
- `images/boa/PXL_20260820_165909161.jpg` — 1.15 mm.
- `images/boa/PXL_20260820_165926746.jpg` — 2.21 mm.

## Current BOA seat-gauge experiment

The four coupons test the assumption that the upper pocket is the larger 20.45 mm step and the lower pocket is the smaller 18.73 mm step. Diametric clearances are:

| Gauge | Added clearance | Upper pocket | Lower pocket |
|---|---:|---:|---:|
| 1 | +0.10 mm | 20.55 mm | 18.83 mm |
| 2 | +0.30 mm | 20.75 mm | 19.03 mm |
| 3 | +0.50 mm | 20.95 mm | 19.23 mm |
| 4 | +0.70 mm | 21.15 mm | 19.43 mm |

Each coupon has an integral raised number. The combined plate is approximately 92 x 73.99 x 5.6 mm; individual coupons are approximately 44 x 31.99 x 5.6 mm. All five STL files were checked with trimesh and are watertight.

Print the combined plate in black PLA, flat on the bed, at 0.20 mm layers, no supports, 100% scale; a brim should not normally be needed. Try gauges in numerical order using light finger pressure only. Do not force, twist, or pry the dial into a coupon. Record:

1. The first gauge that allows the underside to sit fully flat.
2. Whether it rocks or has obvious radial play.
3. Whether lace routing is obstructed.
4. Clear photos from the top and side while seated.

These coupons **do not click or retain the dial**. If none seats, stop: the stepped-diameter order or the interpretation of the underside may be wrong.

Generate the plate with:

```sh
nix develop -c uv run --project projects/collar python -m collar.boa_seat_gauges
```

## Update 2026-09-26: aftermarket dial, slide-in slot closure

The S2-S receiver work and seat gauges are superseded. The user now has an aftermarket BOA-style dial: pop release (tighten-only ratchet until the knob pops, then all tension drops), fabric lace.

Measured: base 37.37 mm round, 39.65 mm across the ear with two small holes, flange 0.94 mm (read edge-on; confirm), lace 1.16 mm.

Chosen closure: the lace is tied permanently to the far segment and the whole dial base slides into a U-shaped slot on the near segment, open end facing away from the seam. Lace tension pulls the disc into the closed end; popping the dial releases the collar with the disc still seated, then the disc slides out. Lips over the flange resist the tipping moment from lace exits above the flange. A flat pad is needed because the brace face is curved (about 3 mm sagitta across 37 mm). Earlier ideas (loose lace bight onto a ramped cleat, S2-S snap receiver) are parked.

Test coupons: `src/collar/boa_slot_gauges.py` writes `build/boa-slot-gauges/` (four numbered flat coupons, slot width 37.67 to 38.27 mm, lip gap 1.14 to 1.44 mm, 1.5 mm lip overlap). Housing diameter at the flange is an estimate (31 mm) until measured. No anti-rotation key yet; the ear holes are a candidate detent.

Series 1 result (printed 2026-09-26, PLA+, 0.2 mm): the disc seated in gauges 1 to 3. Gauge 1 (37.67 mm slot, 1.0 mm lip gap, 1.5 mm overlap) fit best, and the lips had about 1 mm per side to spare. Under lace tension the trailing (ear) end lifted, because the laces ran over the lip top and pulled high. Series 2 (`build/boa-slot-gauges-v2/`) keeps gauge 1's fit, tests lip overlap of 2.0, 2.5 and 3.0 mm, and drops each lace below the flange rim through a notch in the closed-end wall (lace spacing estimated at about 27 mm from the photo). Gauge 4 is a no-notch control at 2.5 mm overlap.

The user prefers one coupon per question. Series 2 plate is generated but not printed; first print `build/boa-lip-ladder/boa-lip-ladder.stl` (`src/collar/boa_lip_ladder.py`), a stepped lip at 2.0 to 4.0 mm overlap that measures how far the lip can reach before hitting the housing. Then print a single slot coupon at the chosen overlap with lace notches.

Ladder result: the 4.0 mm step cleared. Calipers: barrel 26.84 mm, 28.27 mm across the lace-exit bosses (flange ring 4.55 mm). Next single coupon is `build/boa-slot/boa-slot-v3.stl` from `src/collar/boa_slot_gauges.py` (rewritten as a one-coupon generator; the unprinted series-2 plate code is gone): 37.67 mm slot, 1.2 mm lip gap, 4.0 mm side lips ending 4 mm past centre, lip removed around the closed end, lace notches spanning 8 to 18.5 mm each side of a 16 mm centre wall.

v3 result: fit and worked, but under tension the flange climbed over the centre end block (no lip there), and the 4 mm cantilever lips curled up while printing. v4 (`build/boa-slot/boa-slot-v4-plate.stl`) is a flat base plus two flat side-lip rails clamped with four M3 screws and nuts, so the side lips have no overhang; 1.0 mm gap, 4.0 mm side lips, and a 2.0 mm end lip on the base's end block with a 1.2 mm gap. This base-plus-rails stack is the intended construction for the final receiver cartridge.

v4 result: works. Under lace tension the trailing edge barely lifts, so the lift problem is closed. The base holes (3.4 mm through 2.6 mm) could not take the user's heat-set inserts, which measure 5.04 mm OD by 4 mm long. v5 (`build/boa-slot/boa-slot-v5-plate.stl`) keeps the v4 slot and adds a 3.6 mm floor (4.6 mm base) with 4.4 mm insert holes through it; the rails keep 3.4 mm clearance holes.

Brace architecture (2026-09-26, proposed after v4 worked): one print, a chain of rigid segments joined by vertical print-in-place hinges (interleaved knuckles with 45 degree cone pivots), so nothing can fall apart and no hardware joins segments. The hinge axis sits 1.25 mm inside the outer surface: the chain opens outward freely for putting it on, and closing is stopped by the inner end faces meeting at the designed ring shape, so every joint is a hard minimum-circumference stop. The BOA only pulls the single entry seam closed (slot cartridge on one side, lace anchor on the other). With every joint against its stop and the seam closed, the ring is rigid, because a closed ring's turning angles sum to 360 degrees and none can close further. Over-tightening loads the stops and never squeezes the neck. First test piece: `build/hinge-coupon/hinge-coupon-v1.stl` from `src/collar/hinge_coupon.py`, two 30 degree segments at the real 52 mm inner radius, 8 mm wall, 36 mm tall. Code checks: at least 0.30 mm clearance in the print pose, flush at closed, 9.7 mm3 overlap 1 degree past closed, and 145 degrees of free opening. Not yet printed. Open questions: where the seam goes (front quarter recommended), and whether the external knuckle rib (2.25 mm proud) looks acceptable.

Brace direction revised (2026-09-27): the user rejected the print-in-place hinge as too bulky and chose an organic, cord-strung band modeled on a reference collar (domed segments in the channel between the flares, a smooth dial pod). Look study: `src/collar/cord_brace.py` writes `build/cord-brace/` (preview.png, a GLB, and part STLs in the sleeve's local frame). Current layout, all approved by the user: four domed segments (8 mm thick at the ends, 10 mm in the middle, 1.5 mm vertical crown, 36 mm tall, about 49 mm long, 1.5 mm grooves); a 104 mm dial pod centred at the back over the sleeve's rear opening, 42 mm tall at the dial and tapering elliptically to 36 mm at its ends, no thicker than a segment, 2.0 mm off the sleeve; a 40 mm anchor piece; and a 3 mm seam between pod and anchor at about -35 degrees. CAD checks: no part overlaps a neighbour or the sleeve, and the gaps are 1.45 mm. Fillets fell back to 2.25 mm on the pod and 1.88 mm on the anchor.

Intended mechanics, not yet modeled: two low-stretch cords (paracord-class) through every part, just inside the outer surface, top and bottom. They act as the hinge line (so the chain opens without changing cord length), carry the hoop load, and keep parts captive. The inner end faces meet at the designed shape as the per-joint minimum-circumference stop, and the BOA closes the single seam. Because the pod sits beside the seam, the slot must turn vertical and open at the top: a sideways-opening slot would face into the next segment. The disc drops in from above, the lace pulls it against the seam-side wall (lace notches and a short lip go there), and the lip on the side away from the seam holds the trailing edge down. The 37.67 mm pocket, 1.0 mm lip gap and lips over the flange carry over from v4/v5. Part end faces are currently radial cuts; for printing they need to be square to the surface, because they are the stops.

Pod slot coupon v6 (`src/collar/pod_slot_coupon.py`, `build/pod-slot/pod-slot-v6-plate.stl`): the v5 fit turned so the slot opens at the top. The seam side carries the lace notches and the 2 mm end lip on the base; a 4 mm lid lip runs the full height of the trailing side and around the lower arc; 3x M3 heat-set inserts. Print in PETG, the pod's final material. Material plan agreed with the user: PETG for the pod, rails and anchor (tough, kind to the lace, holds inserts, slightly flexible); PETG-CF for the four segments (stiff, matte); no PLA in worn parts, because PLA creeps under sustained lace tension at body temperature. PETG-CF needs a hardened nozzle, and cord tunnel exits in CF parts should be chamfered.

Dial mounting decision (2026-09-27): the dial base is captured permanently in the pod. A top-opening slot was ruled out: the upper flare widens past the seat plane above about 29 mm, so a sliding disc would collide with it for any centre height between about 10 and 56 mm. Putting the collar on or taking it off relies on the popped dial paying out lace to open the seam. The needed pay-out (about 12-15 cm) has not been measured yet. `src/collar/dial_pod.py` builds the printable pod: an oval seat (39.97 x 37.67 x 1.0 mm) cut along a plane 4.75 mm below the curved face; a separate curved lid over the trailing half (2x M3 into heat-set inserts, M3x6); the pod's own lap over the seam half; lace windows either side of a 16 mm centre block. Checks: lid at least 1.87 mm thick over the flange, lap 1.2 mm, floor 3.95 mm, 2.92 mm of material behind the inserts, no overlap with the dial, lid, sleeve, segment 4 or the anchor. The pod gained 1.5 mm thickness at the dial, a 43 mm height and a 0.5 mm crown. Outputs: `build/dial-pod/dial-pod-print-upright.stl` (PETG, upright, tree supports from the build plate under the tapered underside) and `dial-pod-lid-print-flat.stl`. Not yet in the pod: cord knot holes at the trailing end, lace guides to the seam, and a seam stop face squared to the surface.

Printable brace (2026-10-04, `src/collar/brace_parts.py` -> `build/brace-parts/`): anchor, five segments, a 62 mm dial pod and its lid. The user chose 8 mm of squeeze. The chain's length is fixed by the parts and cords, so tightening only closes the seam: 13.9 mm open when wrapped loosely, about 5 mm to reach the sleeve, then 8 mm of squeeze before the pod's and anchor's seam faces meet flush. That seam is the hard minimum-circumference stop (checked: 12.88 mm gap as built, 0.0 mm gap and no overlap at the squeeze limit). Each joint closes 1.9 degrees at the limit, and its wedge allows 2.47 degrees, so the seam always decides. Joint faces are two planes meeting on the cord line, 3.5 mm inside the outer edge: the inner wedge face is the stop, and the outer relief face allows 30 degrees of opening (28 checked clear). Joint contact is checked by point sampling, because an OCC boolean silently returned an empty intersection for segment-1|segment-2. Cords: two 4 mm paracords in 4.6 mm tunnels at +/-12 mm, from knot pockets in the anchor (12 mm from its joint end) to knot pockets in the pod (5.5 mm in), all open on the inner face. Each cord has its own 7 mm wide stadium pocket running from |z| = 14.5 mm (2.5 mm past the cord) toward mid-height down to |z| = 5 mm. It has to stop 1 mm inside the 2.5 mm edge round: on the 36 mm anchor, a pocket touching that boundary made the inner face unmeshable (691 open edges, and the STEP read back invalid), and overlapping cylinders were worse. All eight print files are now watertight STLs and every STEP reads back valid; `build/print-plate-petg/` holds the eight files for one PETG plate. The first printed pod and anchor (2026-10-05) had a single pocket at mid-height that did not reach either tunnel; fixed in code, and both parts need reprinting. Lace: out through the pod's windows at the seam face, into two holes in the anchor, around a vertical M3x20 post in a pocket that opens on the inner face (the user's kit tops out at M3x20). The screw goes in from the top through a 5.8 mm counterbore whose floor sits at z = 9.9 mm, leaving a 3.4 mm wall above the pocket, and threads into an M3 hex nut that slides into a 5.7 mm slot from the inner face, 1 mm below the pocket floor. The lace strands converge to +/-4.5 mm inside the anchor to keep the pocket short. User's hardware kit: M3 screws 4/6/10/16/20 mm, M3 nuts, 7 mm washers, M3 inserts 5 mm OD x 4 mm (kit recommends a 4.6 mm hole, at least 4.1 mm deep, 2 mm wall) and 4.6 mm OD x 5.7 mm. Pod insert holes changed from 4.4 to 4.6 mm. Walls: 1.2 mm skin over the cord tunnels at segment ends, 2.2 mm under them, but only 1.0 mm under the cord tunnel in the pod. The pod STL keeps 12 bad mesh edges where its taper meets the end faces (the solid is valid), so slice the pod from the STEP export. networkx was added to the collar project for mesh repair. The viewer artifact (https://claude.ai/artifact/VaZib5DmayZQWWjeVrTJRB) shows these parts, with tightening below zero on the slider.

Lid front hook (2026-10-05): with screws only at the back, the lid's front edge could lift. The lid now has two tongues (3.5 mm long, 1.2 mm thick, at |v| 16.5-20 mm) that slide into slots under the pod's lip (0.25 mm clearance, 3.3 mm of lip above). Assembly: hook the front in, lay it flat, screw the back. The lace windows were narrowed to |v| 8-16 mm to make room (the strands leave the dial near 12 mm). The user cancelled the PETG-CF segment print and is printing every part in one PETG plate, because the stock nozzle is yellow (probably brass, not confirmed).

Still open: housing diameter at flange, lace exit height, ear hole size and spacing, the far-segment lace anchor (stopper knot behind a rounded hole plus a clamp), and the single-seam rigid-arc brace layout.

## Recommended next steps

1. Have the user print and evaluate `boa-s2s-seat-gauges-1-to-4-plate.stl`.
2. Use the winning seat clearance to design a second small numbered PLA series that varies only snap-tab/retention geometry and includes an intentional release path.
3. Once retention is repeatable, package the receiver as a replaceable cartridge attached to a rear brace saddle with the user's M3 screws and heat-set inserts.
4. Route two lace runs symmetrically around the segmented brace. Keep the BOA load path in the outer brace; do not pull directly on thin TPU sleeve walls.
5. Add a mechanically independent minimum-circumference stop and a rapid, accessible release before any worn tension test.
6. Bench-test on the neck proxy or a rigid circumference fixture before low-tension supervised human fitting.

Do not integrate the BOA receiver directly into all eight brace segments yet; the interface is still experimental and should remain cheap to reprint.

## Hardware available

The user has an M3 assortment including socket-head screws, nuts, washers, and heat-set inserts. Prefer these for the replaceable receiver cartridge and rear saddle. Confirm actual screw lengths and insert outside dimensions when the mount reaches detail design.

## Safety constraints

This is a neck-worn tightening device. Treat these as non-negotiable design requirements:

- A hard minimum circumference must prevent dangerous tightening independently of the dial or lace.
- Release must be reachable immediately by the wearer and by another person.
- No geometry may obstruct breathing, swallowing, jaw movement, or rapid removal.
- Sharp edges, exposed wire ends, and concentrated posterior pressure are unacceptable.
- Validate on a rigid proxy first, then use only very low tension for initial supervised fit checks.
- Do not treat tooth removal, software instructions, or user judgment as the sole over-tightening safeguard.

## Verification and worktree state

On 2026-09-16:

```text
nix develop -c uv run --project projects/collar python -m unittest discover -s projects/collar/tests
Ran 8 tests in 0.010s — OK
```

The worktree contains substantial uncommitted collar work. Preserve it. At handoff time the tracked modifications included `README.md`, `config/melissa.json`, `pyproject.toml`, and `tests/test_symmetry.py`; untracked work included the newer generators, BOA documentation/photos, ratchet photos, and `stl/boa-buckle.stl`. Inspect `git status --short projects/collar` before editing and do not discard unrelated user changes.

## Research references

- Official BOA S2-S repair guide: https://www.boafit.com/en-gb/support/repair-guides/S2S-repair-guide
- Official S2-S repair PDF: https://www.boafit.com/sites/boafit/files/2019-03/S2S_Prelooped_1000049_web.pdf
- University of Idaho thesis record: https://verso.uidaho.edu/esploro/outputs/graduate/Additions-and-Improvements-to-the-Mechanical/996638120301851
- Thesis PDF: https://objects.lib.uidaho.edu/etd/pdf/Townsend_idaho_0089N_11915.pdf

## Historical Solo note

The older Solo scratchpad named `POSTURE COLLAR (SYSTEM ARCHITECTURE SPECIFICATION)` is useful as initial intent but is no longer authoritative. In particular, its off-the-shelf ladder-ratchet recommendation predates the physical buckle failure and BOA pivot. This handoff is the current source of project status.

## 2026-10-07: anchor v2, knot catch replaces the post

With the lace looped around the M3x20 post, the 254 mm the popped dial pays out
was not enough to clear Melissa's head. The anchor now catches the lace on its
outer face: a mouth at the seam face (|v| up to 14) narrows into a 2.8 mm channel
(floor at OUTER_EDGE - 3.8) ending in an 8 mm wide knot pocket at u 9-18
(floor 3 mm above the inner face). A figure-eight tied in the doubled loop drops
in; popped, it lifts out and the chain opens fully. Post, nut slot, inner lace
pocket and seam-face grooves are gone, so the M3x20 and nut are no longer used.
Probed in the STL: channel floor about 4.6 mm below the surface, pocket u 9.5-17.5,
watertight single body. Only the anchor needs reprinting:
`build/print-plate-petg/anchor-v2-lace-catch-print-upright.stl`.
Open risk: the knot bears on only about 0.85 mm each side of the channel; if a
figure-eight squeezes through, use a double figure-eight or narrow the channel.

Revised the same day (v3, user asked for a narrow straight slot and traps):
straight slot from the seam face, 1.4 mm wide at the surface and 3.0 mm
underneath (2.3 mm deep base, 45 degree roof on the upper side so it prints
upright without support), into a round knot pocket at u 12.5 that is 4.0 mm
across at the surface and 7.0 mm underneath (45 degree cone). Cross-sections
probed in the STL match. File: `anchor-v3-trap-catch-print-upright.stl`.
Untested: whether a figure-eight in the doubled lace squeezes through the
4 mm neck by thumb, and whether the doubled lace presses through the 1.4 mm
slot one strand at a time.
