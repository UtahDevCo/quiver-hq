"""Two-piece slide-in slot coupon for the aftermarket BOA-style dial base.

The dial's smooth-backed base (37.37 mm round, 0.94 mm flange) slides into a
U-shaped pocket from the open end.  Lips over the flange resist the tipping
moment from lace tension, which acts above the flange and lifts the trailing
(ear) edge.  Lace tension pulls the disc into the closed end; the dial's pop
release drops all tension, after which the disc slides back out.

The coupon is a flat base (floor plus the flange pocket, open on top) and a
pair of flat side-lip rails, each held by two M3 screws into brass heat-set
inserts in the base (measured 5.04 mm OD, 4 mm long).  The
open end must stay clear for the housing and the closed end for the laces, so
the lid cannot join into one piece.  The side
lips have no overhang, so their gap is the printed pocket depth and nothing
sags or curls.  The end lip sits on the base's end block as a short 2 mm
cantilever, because joining it to the lid would roof over the lace notches.  The final receiver is meant to be the same stack screwed to a flat
pad on a brace segment.

History (all PLA+, 0.2 mm layers):
- Series 1: four one-piece coupons at 1.5 mm lip overlap.  Best fit was a
  37.67 mm slot with a 1.0 mm lip gap.  The trailing edge lifted because the
  laces ran over the lip top and pulled high.
- Lip ladder (`boa_lip_ladder.py`): a 4.0 mm overlap still cleared.  Calipers:
  barrel 26.84 mm, 28.27 mm across the lace-exit bosses.
- v3: one piece, 4.0 mm side lips, no lip at the closed end, wide lace notches.
  Fit and worked, but the flange climbed over the centre end block under
  tension, and the 4 mm cantilever lips curled up as they printed.
- v4: two flat pieces, 1.0 mm side-lip gap, 4.0 mm side lips, and a 2.0 mm
  end lip on the base with a 1.2 mm gap to allow for sag.  The trailing edge
  barely lifts under tension: the lift problem is solved.  The base holes were
  3.4 mm through a 2.6 mm base, too small and shallow for the inserts.
- v5 (this file): same slot; 3.6 mm floor so the base is 4.6 mm thick at the
  holes, and 4.4 mm insert holes through the base.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq

from .config import PROJECT_ROOT


BASE_DIAMETER_MM = 37.37
FLANGE_THICKNESS_MM = 0.94
WIDEST_HOUSING_MM = 28.27  # across the lace-exit bosses

SLOT_WIDTH_MM = 37.67
LIP_GAP_MM = 1.0
SIDE_LIP_OVERLAP_MM = 4.0
END_LIP_OVERLAP_MM = 2.0
END_LIP_EXTRA_GAP_MM = 0.2
FLOOR_MM = 3.6
LID_MM = 1.6
MARGIN_MM = 7.0

# Side lips stop this far past the disc centre toward the closed end; beyond
# it the laces cross the flange ring freely.
SIDE_LIP_END_X_MM = 4.0
# The centre end block (|y| < this) stops the disc and carries the end lip.
# Either side of it, notches drop each lace below the flange rim.
END_BLOCK_HALF_WIDTH_MM = 8.0
NOTCH_FLOOR_Z_MM = FLOOR_MM - 0.6

SCREW_CLEARANCE_MM = 3.4
INSERT_HOLE_MM = 4.4  # for 5.04 mm OD x 4 mm knurled M3 inserts
SCREW_INSET_MM = 3.5

LABEL = "v5"


def _u_shape(width: float, open_length: float, z0: float, height: float) -> cq.Workplane:
    """Semicircular closed end at +X around the origin, open toward -X."""
    circle = cq.Workplane("XY").workplane(offset=z0).circle(width / 2).extrude(height)
    channel = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(-open_length / 2, 0)
        .rect(open_length, width)
        .extrude(height)
    )
    return circle.union(channel)


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center((x0 + x1) / 2, (y0 + y1) / 2)
        .rect(x1 - x0, y1 - y0)
        .extrude(z1 - z0)
    )


def _extent() -> tuple[float, float, float]:
    half = SLOT_WIDTH_MM / 2 + MARGIN_MM
    return -half - 6.0, half, half


def _screw_holes(body: cq.Workplane, z1: float, diameter: float) -> cq.Workplane:
    x0, x1, half = _extent()
    for x in (x0 + SCREW_INSET_MM, x1 - SCREW_INSET_MM):
        for y in (-half + SCREW_INSET_MM, half - SCREW_INSET_MM):
            hole = (
                cq.Workplane("XY")
                .workplane(offset=-1.0)
                .center(x, y)
                .circle(diameter / 2)
                .extrude(z1 + 2.0)
            )
            body = body.cut(hole)
    return body


def _lace_notches(body: cq.Workplane, z1: float) -> cq.Workplane:
    _, x1, _ = _extent()
    edge = SLOT_WIDTH_MM / 2 + 0.5
    for y0, y1 in ((END_BLOCK_HALF_WIDTH_MM, edge), (-edge, -END_BLOCK_HALF_WIDTH_MM)):
        body = body.cut(_box(SIDE_LIP_END_X_MM, x1 + 1.0, y0, y1, NOTCH_FLOOR_Z_MM, z1 + 1.0))
    return body


def _solids(body: cq.Workplane, name: str, count: int) -> cq.Shape:
    shape = body.val()
    if not shape.isValid() or len(shape.Solids()) != count:
        raise RuntimeError(f"{name} should be {count} valid solid(s)")
    return shape


def make_base() -> cq.Shape:
    x0, x1, half = _extent()
    top = FLOOR_MM + LIP_GAP_MM
    body = _box(x0, x1, -half, half, 0.0, top)
    body = body.cut(_u_shape(SLOT_WIDTH_MM, x1 - x0 + 10.0, FLOOR_MM, LIP_GAP_MM + 0.01))
    body = _lace_notches(body, top)

    lip_z = top + END_LIP_EXTRA_GAP_MM
    rim = SLOT_WIDTH_MM / 2
    block = END_BLOCK_HALF_WIDTH_MM
    body = body.union(_box(rim + 0.05, x1, -block, block, top - 0.01, lip_z))
    body = body.union(_box(rim - END_LIP_OVERLAP_MM, x1, -block, block, lip_z, top + LID_MM))
    return _solids(_screw_holes(body, top + LID_MM, INSERT_HOLE_MM), "Slot base", 1)


def make_lid() -> cq.Shape:
    side_opening = SLOT_WIDTH_MM - 2 * SIDE_LIP_OVERLAP_MM
    if side_opening <= WIDEST_HOUSING_MM + 0.5:
        raise ValueError("Side lip opening would not clear the dial housing")

    x0, x1, half = _extent()
    body = _box(x0, x1, -half, half, 0.0, LID_MM)
    body = body.cut(_u_shape(side_opening, x1 - x0 + 10.0, -0.5, LID_MM + 1.0))
    edge = SLOT_WIDTH_MM / 2 + 0.5
    body = body.cut(_box(SIDE_LIP_END_X_MM, x1 + 1.0, -edge, edge, -0.5, LID_MM + 0.5))
    body = _screw_holes(body, LID_MM, SCREW_CLEARANCE_MM)

    label = (
        cq.Workplane("XY")
        .workplane(offset=LID_MM)
        .center(-14.0, half - SCREW_INSET_MM)
        .text(LABEL, 5.0, 0.6, combine=True)
    )
    return _solids(body.union(label), "Slot lid rails", 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "build" / "boa-slot")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    base, lid = make_base(), make_lid()
    _, _, half = _extent()
    cq.exporters.export(base, str(args.output_dir / f"boa-slot-{LABEL}-base.stl"))
    cq.exporters.export(lid, str(args.output_dir / f"boa-slot-{LABEL}-lid.stl"))
    plate = cq.Compound.makeCompound([base, lid.translate(cq.Vector(0, 2 * half + 6.0, 0))])
    cq.exporters.export(plate, str(args.output_dir / f"boa-slot-{LABEL}-plate.stl"))
    (args.output_dir / f"boa-slot-{LABEL}.json").write_text(
        json.dumps(
            {
                "slot_width_mm": SLOT_WIDTH_MM,
                "lip_gap_mm": LIP_GAP_MM,
                "side_lip_overlap_mm": SIDE_LIP_OVERLAP_MM,
                "side_lip_opening_mm": round(SLOT_WIDTH_MM - 2 * SIDE_LIP_OVERLAP_MM, 2),
                "end_lip_overlap_mm": END_LIP_OVERLAP_MM,
                "end_block_width_mm": 2 * END_BLOCK_HALF_WIDTH_MM,
                "screws": "4x M3 into heat-set inserts; base insert holes 4.4 mm through 4.6 mm, rail clearance 3.4 mm",
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Wrote base, lid and plate to {args.output_dir}")


if __name__ == "__main__":
    main()
