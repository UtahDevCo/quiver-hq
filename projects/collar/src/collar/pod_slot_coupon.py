"""Flat coupon of the dial pod's top-opening slot (v6).

In the brace the dial pod sits beside the entry seam, so a slot that opens
sideways would face into the neighbouring segment.  This slot opens at the top
instead: the disc drops in from above, gravity keeps it down, and lace
tension pulls it sideways against the seam-side wall (+X here).

Same fit as the proven v4/v5 two-piece slot (`boa_slot_gauges.py`): a
37.67 mm pocket, 1.0 mm lip gap, a flat base with 4.4 mm heat-set insert holes,
and a flat lid.  Rotating the slot moves the features:
- seam side (+X): lace notches drop each lace below the flange rim either side
  of a 16 mm centre block, which carries the 2 mm end lip (on the base);
- trailing side (-X), the edge lace tension lifts: a 4 mm lid lip runs its
  full height, directly behind that edge;
- bottom arc: the lid lip continues around, so the disc cannot rock out.

The dial base is oval: 37.37 mm across and 39.65 mm across the ear.  With
the lace exits toward the seam the ear points at the trailing wall, so v7
extends the pocket and the channel 2.3 mm toward the trailing side (v6's round
pocket only accepted the disc turned sideways).

Bench coupon only: flat, no pod curvature, and no detent against riding up.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq

from .boa_slot_gauges import (
    END_BLOCK_HALF_WIDTH_MM,
    END_LIP_EXTRA_GAP_MM,
    END_LIP_OVERLAP_MM,
    FLOOR_MM,
    INSERT_HOLE_MM,
    LID_MM,
    LIP_GAP_MM,
    MARGIN_MM,
    NOTCH_FLOOR_Z_MM,
    SCREW_CLEARANCE_MM,
    SCREW_INSET_MM,
    SIDE_LIP_END_X_MM,
    SIDE_LIP_OVERLAP_MM,
    SLOT_WIDTH_MM,
    WIDEST_HOUSING_MM,
    _box,
    _solids,
)
from .config import PROJECT_ROOT


MOUTH_EXTRA_MM = 6.0
BASE_ACROSS_EAR_MM = 39.65
# How far the ear reaches past the round flange, toward the trailing side.
EAR_EXTRA_MM = BASE_ACROSS_EAR_MM - 37.37
LABEL = "v7"


def _extent() -> tuple[float, float, float, float]:
    half = SLOT_WIDTH_MM / 2 + MARGIN_MM
    return -half - EAR_EXTRA_MM, half, -half, half + MOUTH_EXTRA_MM


def _slot(width: float, z0: float, height: float, ear: float = 0.0) -> cq.Workplane:
    """Seat at the origin, stretched `ear` toward -X, with a channel up to +Y."""
    _, _, _, y1 = _extent()
    seat = cq.Workplane("XY").workplane(offset=z0).circle(width / 2).extrude(height)
    if ear:
        seat = seat.union(seat.translate((-ear, 0, 0)))
        seat = seat.union(_box(-ear, 0.0, -width / 2, width / 2, z0, z0 + height))
    return seat.union(_box(-width / 2 - ear, width / 2, 0.0, y1 + 1.0, z0, z0 + height))


def _screw_holes(body: cq.Workplane, z1: float, diameter: float) -> cq.Workplane:
    x0, x1, y0, y1 = _extent()
    for x, y in (
        (x0 + SCREW_INSET_MM, y0 + SCREW_INSET_MM),
        (x0 + SCREW_INSET_MM, y1 - SCREW_INSET_MM),
        (x1 - SCREW_INSET_MM, y0 + SCREW_INSET_MM),
    ):
        hole = (
            cq.Workplane("XY")
            .workplane(offset=-1.0)
            .center(x, y)
            .circle(diameter / 2)
            .extrude(z1 + 2.0)
        )
        body = body.cut(hole)
    return body


def make_base() -> cq.Shape:
    x0, x1, y0, y1 = _extent()
    top = FLOOR_MM + LIP_GAP_MM
    body = _box(x0, x1, y0, y1, 0.0, top)
    body = body.cut(_slot(SLOT_WIDTH_MM, FLOOR_MM, LIP_GAP_MM + 0.01, EAR_EXTRA_MM))

    edge = SLOT_WIDTH_MM / 2 + 0.5
    block = END_BLOCK_HALF_WIDTH_MM
    for n0, n1 in ((block, edge), (-edge, -block)):
        body = body.cut(_box(SIDE_LIP_END_X_MM, x1 + 1.0, n0, n1, NOTCH_FLOOR_Z_MM, top + 1.0))

    lip_z = top + END_LIP_EXTRA_GAP_MM
    rim = SLOT_WIDTH_MM / 2
    body = body.union(_box(rim + 0.05, x1, -block, block, top - 0.01, lip_z))
    body = body.union(_box(rim - END_LIP_OVERLAP_MM, x1, -block, block, lip_z, top + LID_MM))
    return _solids(_screw_holes(body, top + LID_MM, INSERT_HOLE_MM), "Pod slot base", 1)


def make_lid() -> cq.Shape:
    opening = SLOT_WIDTH_MM - 2 * SIDE_LIP_OVERLAP_MM
    if opening <= WIDEST_HOUSING_MM + 0.5:
        raise ValueError("Lip opening would not clear the dial housing")

    x0, x1, y0, y1 = _extent()
    edge = SLOT_WIDTH_MM / 2 + 0.5
    body = _box(x0, x1, y0, y1, 0.0, LID_MM)
    body = body.cut(_slot(opening, -0.5, LID_MM + 1.0))
    body = body.cut(_box(SIDE_LIP_END_X_MM, x1 + 1.0, -edge, y1 + 1.0, -0.5, LID_MM + 0.5))
    body = _screw_holes(body, LID_MM, SCREW_CLEARANCE_MM)
    label = (
        cq.Workplane("XY")
        .workplane(offset=LID_MM)
        .center(-8.0, y0 + SCREW_INSET_MM)
        .text(LABEL, 5.0, 0.6, combine=True)
    )
    return _solids(body.union(label), "Pod slot lid", 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "build" / "pod-slot")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    base, lid = make_base(), make_lid()
    x0, x1, _, _ = _extent()
    cq.exporters.export(base, str(args.output_dir / f"pod-slot-{LABEL}-base.stl"))
    cq.exporters.export(lid, str(args.output_dir / f"pod-slot-{LABEL}-lid.stl"))
    plate = cq.Compound.makeCompound([base, lid.translate(cq.Vector(x1 - x0 + 6.0, 0, 0))])
    cq.exporters.export(plate, str(args.output_dir / f"pod-slot-{LABEL}-plate.stl"))
    (args.output_dir / f"pod-slot-{LABEL}.json").write_text(
        json.dumps(
            {
                "slot_width_mm": SLOT_WIDTH_MM,
                "slot_length_along_pull_mm": round(SLOT_WIDTH_MM + EAR_EXTRA_MM, 2),
                "lip_gap_mm": LIP_GAP_MM,
                "trailing_lip_overlap_mm": SIDE_LIP_OVERLAP_MM,
                "lip_opening_mm": round(SLOT_WIDTH_MM - 2 * SIDE_LIP_OVERLAP_MM, 2),
                "seam_end_lip_overlap_mm": END_LIP_OVERLAP_MM,
                "screws": "3x M3 into heat-set inserts",
                "material": "PETG (the pod's final material)",
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Wrote base, lid and plate to {args.output_dir}")


if __name__ == "__main__":
    main()
