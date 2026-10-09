# Collar project handoff, 2026-10-09

Abandoned approaches (S2-S receiver coupons, slide-in slot coupons, the
ladder-strap ratchet brace, print-in-place hinges) were removed in the cleanup
after commit `ee39148`. That commit has their code and the full history of this
file.

## Status

- **Inner sleeve:** printed in TPU 95A and fits. Treat `full_sleeve` and the
  `full_sleeve` block of `config/melissa.json` as the validated baseline.
  Printed upright on the lower flare, 0.20 mm layers, 5 mm brim, no supports.
- **Outer brace:** every part printed in PETG on 2026-10-05 (Qidi X-Plus 4,
  stock nozzle, probably brass). Anchor v3 (knot cave, slot through its skin,
  square-knot cord channel, engraved A) printed 2026-10-08 in 52 min with
  supports off and works: the knot drops in the window, the lace presses into
  the slot, and tension slides the knot under the cover. The slicer warns about
  floating regions on it; that is the slit's overhanging edge and printed fine.
  The other parts still lack the engraved labels unless reprinted.
  `build/print-plate-petg/` holds the current set.
- No tensioned fitting on Melissa yet.

## Brace design

Anchor, five domed segments, and a 62 mm dial pod with a separate lid, laid out
by arc length on the sleeve's smoothed outer profile. The pod is centred at the
back and the seam sits between pod and anchor.

- **Cords:** two 4 mm paracords in 4.6 mm tunnels at z = ±12 mm, 3.5 mm inside
  the outer edge. In the pod each ends in its own figure-eight pocket (7 mm
  stadium on the inner face from |z| 14.5 to 5 mm, 5.5 mm from the pod's end).
  In the anchor both ends meet in one 10.5 mm wide channel from z = -14.5 to
  +14.5 mm (u = 24.5 to 35.5 mm, 4.5 mm from the joint end) and are tied
  together with a square knot. It sits 8 mm from the joint end to make room for
  the lace knot cave; about 1.6 mm of wall separates the two. Pockets must stop 1 mm inside the 2.5 mm edge round, or the
  inner face becomes unmeshable.
- **Labels:** engraved 0.6 mm into the inner face, 7 mm text, readable from
  inside the ring: A (anchor, 6.5 mm from its seam face), 1 to 5 (segments,
  mid-arc) and P (pod, between its knot pockets). The lid has none: it is
  1.62 mm thick at its thinnest. Wall left behind a label: anchor 3.4 mm,
  pod 7.1 mm, segments 9.1 mm.
- **Joints:** two planes meeting on the cord line. The inner wedge face is the
  stop and the outer relief opens 30 degrees.
- **Seam stop:** wrapped loosely the seam is 13.9 mm open; about 5 mm brings the
  brace onto the sleeve, then 8 mm of squeeze before the seam faces meet flush.
  Each joint closes 1.9 degrees at that point and its wedge allows 2.47, so the
  seam always decides. Checked: 12.88 mm gap as built, 0.0 mm and no overlap
  at the limit. Joint contact is checked by point sampling, because an OCC
  boolean silently returned an empty intersection once.
- **Dial pod:** the dial is captured permanently on a flat seat 5.7 mm below
  the curved face (oval pocket 39.97 x 37.67 x 1.0 mm). The pod's own lap
  covers the seam half, and the lid covers the trailing half. The lid hooks in
  at the front with two tongues and screws down at the back with 2x M3x6 into
  5 x 4 mm heat-set inserts in 4.6 mm holes. The lace windows are at |v| 8 to
  16 mm. Walls: lid at least 1.62 mm over the flange, lap 1.2 mm, floor
  3.0 mm, 2.73 mm behind the inserts, and only 1.0 mm under the cord tunnel in
  the pod.
- **Lace catch (anchor v3):** sized to the measured lace: the doubled lace is
  3.2 mm side by side and the figure-eight in it is 8.45 mm across. A straight
  slot from the seam face slopes into the part at 45 degrees (3.8 mm tall at the
  surface, 3.0 mm deep, both long faces at 45 degrees), swept along the domed
  outer face so its depth stays constant. It opens into a covered knot cave
  (u = 2.5 to 18 mm, 10 mm tall plus a 45 degree gable, about 5.4 mm deep,
  1.6 mm floor, at least 1.4 mm of skin), swept along the floor's offset curve
  so the skin does not thin at the ends. It ends at a 10 mm teardrop window
  centred at u = 18 mm, which leaves about 11 mm of the knot's path covered. The knot drops into the window and lace tension
  slides it under the skin, so loosening the dial to adjust does not free it.
  The lace slot runs on through the skin to the window, so the lace presses
  in from outside along its whole length (no threading); the slit is about
  2.7 mm across square to the slot, far too narrow for the knot. The skin's
  lower edge over the slit is held only at its seam end, about a 6 mm one-sided
  overhang, and the island check finds a 0.2 mm2 sliver there.
  The knot must lie flat (8.45 mm width vertical) to fit the 5.4 mm depth. It
  bears on the cave's
  end, pulling away from the square-knot channel. Earlier versions were sized for a single
  1.16 mm strand and a 4 mm knot opening and did not fit the real lace. Any lip
  over this open-ended slot prints in mid-air, so there is no trap on the slot.
  Layer check (three slice offsets): no floating regions. The A label moved to
  z = -11 mm, below the pocket.
- **Meshes:** all eight print STLs are watertight single bodies (checked
  2026-10-07; the pod's STL used to carry 12 bad edges).

Segment chords between joint lines: 1 = 44.7, 2 = 46.6, 3 = 46.3, 4 = 44.1,
5 = 46.1 mm. Segments 1 and 4 are the curved pair, and 2, 3 and 5 are
interchangeable. The first prints have no labels.

Iterating: `python -m collar.brace_parts --skip-check` takes about 40 s.
The joint and seam checks take about 19 minutes more, so run them before
committing a change to joints, cords or the seam.

## Dial and hardware

- **Dial:** an aftermarket BOA-style dial. It tightens only, until the knob is
  pulled out (popped), which releases all tension. The base is 37.37 mm round
  and 39.65 mm across the ear (two small holes). Flange 0.94 mm, barrel
  26.84 mm, 28.27 mm across the lace bosses. Fabric lace, 1.16 mm, closed
  loop, pays out about 254 mm when popped.
- **Hardware kit:** M3 screws 4/6/10/16/20 mm, M3 nuts, 7 mm washers, heat-set
  inserts 5 x 4 mm (kit hole 4.6 mm, at least 4.1 mm deep, 2 mm wall) and
  4.6 x 5.7 mm. Use the 5 x 4 mm ones, smooth end first.

## Sleeve liner

The printed TPU sleeve is scratchy, so it gets a glued-in liner of thin
vegetable-tanned lambskin (Tandy Veg-Tan Lambskin, 1 oz / 0.4 mm ideal; avoid
chrome-tanned leather, which releases chromium in sweat). `collar.sleeve_liner`
unrolls the sleeve's skin-side surface into 5 butt-seamed panels (about 66 x 77
mm each, P3 centred on the throat) with 6 mm fold allowances over the rims and
the rear-opening ends, and optional 1.6 mm perforations (Craftool punch size
00) on an 8 mm staggered grid. Seam edges stretch under 2 percent; the opening
edges about 3.7 to 3.9 percent, inside the folded allowance. Output:
`build/sleeve-liner/sleeve-liner-pattern.pdf` (page 1 shopping list and steps,
then 1:1 panels with a 50 mm check square). Glue: Barge All-Purpose Cement,
TPU scuffed with 220-grit and wiped with alcohol. 0.4 mm of leather uses about
a fifth of the 2 mm skin clearance; at 0.8 mm, regenerate the sleeve with more
clearance first.

## Open questions

- Reprint segments 1 to 5 and the pod for their engraved labels, or mark the
  printed ones by hand.
- First tensioned fitting: rigid stand-in, then Melissa at light tension.
- Liner: patch-test the leather, then glue it in and check the fit.

## Safety constraints

This is a neck-worn tightening device:

- A hard minimum circumference must prevent dangerous tightening independently
  of the dial or lace (the seam stop).
- Release must be reachable immediately by the wearer and by another person.
- No geometry may obstruct breathing, swallowing, jaw movement or rapid
  removal. No sharp edges or concentrated pressure at the back of the neck.
- Validate on a rigid stand-in first, then use only light tension for
  supervised fittings.

## Artifacts

- Build guide: https://claude.ai/artifact/TKuqMja2Ndq7V2KwcDbT8Q
- Assembly viewer: https://claude.ai/artifact/VaZib5DmayZQWWjeVrTJRB
