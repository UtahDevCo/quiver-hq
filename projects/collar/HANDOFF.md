# Collar project handoff, 2026-10-07

Abandoned approaches (S2-S receiver coupons, slide-in slot coupons, the
ladder-strap ratchet brace, print-in-place hinges) were removed in the cleanup
after commit `ee39148`. That commit has their code and the full history of this
file.

## Status

- **Inner sleeve:** printed in TPU 95A and fits. Treat `full_sleeve` and the
  `full_sleeve` block of `config/melissa.json` as the validated baseline.
  Printed upright on the lower flare, 0.20 mm layers, 5 mm brim, no supports.
- **Outer brace:** every part printed in PETG on 2026-10-05 (Qidi X-Plus 4,
  stock nozzle, probably brass). Since then the anchor gained the lace
  catch and the square-knot cord channel, and every part except the lid
  gained an engraved label. `build/print-plate-petg/` holds the current set.
- No tensioned fitting on Melissa yet.

## Brace design

Anchor, five domed segments, and a 62 mm dial pod with a separate lid, laid out
by arc length on the sleeve's smoothed outer profile. The pod is centred at the
back and the seam sits between pod and anchor.

- **Cords:** two 4 mm paracords in 4.6 mm tunnels at z = ±12 mm, 3.5 mm inside
  the outer edge. In the pod each ends in its own figure-eight pocket (7 mm
  stadium on the inner face from |z| 14.5 to 5 mm, 5.5 mm from the pod's end).
  In the anchor both ends meet in one 10.5 mm wide channel from z = -14.5 to
  +14.5 mm and are tied together with a square knot. The channel keeps the old
  pockets' edge nearest the joint (12 mm + 3.5 mm from the joint end) and grows
  into the body. Pockets must stop 1 mm inside the 2.5 mm edge round, or the
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
- **Lace catch (anchor v3):** a straight slot from the seam face runs into a
  round knot pocket at u = 12.5 mm (4.0 mm across at the surface, 7.0 mm
  underneath, 45 degree cone). The slot is a hook: a 1.4 mm opening, a 45
  degree upper face with no lip, and a 1.2 mm lower lip with a pocket reaching
  2.5 mm down behind it. A lip on the upper side made a floating region when
  printed upright, because the slot is open at both ends (24 mm2 with a flat
  underside, still 4 mm2 with 45 degree faces). The layer-by-layer island check
  now finds none. A figure-eight in the doubled lace presses into the knot
  pocket. With the dial popped it pulls back out and the brace opens fully.
  This replaced a screw post, because the 254 mm of lace the popped dial pays
  out could not clear Melissa's head.
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

## Open questions

- Whether a figure-eight in the doubled lace pushes through the 4 mm knot
  opening by thumb. Go to 4.5 mm if not, or 3.5 mm if it pulls out under
  tension.
- Whether the strands press through the 1.4 mm slot opening and stay behind
  the lower lip. Next step is 1.6 mm.

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
