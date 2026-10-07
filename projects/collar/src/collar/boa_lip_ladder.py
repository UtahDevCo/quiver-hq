"""Stepped lip-overlap ladder for the aftermarket dial base.

One bar with a straight lip along its outer edge and a flange groove under it
whose depth steps 2.0 to 4.0 mm.  Slide the flange sideways under the lip at
each step: if a gap remains between the housing and the lip edge, the flange
bottomed out first and that overlap fits; if the housing touches the lip edge,
the step is deeper than the flange ring.  The deepest step with a gap is the
usable lip overlap.

The lip gap here is deliberately looser than the slot coupons' 1.0 mm so a
drooping cantilever cannot block the flange; this coupon measures reach only.
A 1.6 mm apron in front keeps the disc level with the groove floor.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq

from .config import PROJECT_ROOT


STEPS_MM = (2.0, 2.5, 3.0, 3.5, 4.0)
# A round 37.37 mm flange stepping 0.5 mm deeper cannot reach the shallower
# neighbour's back wall once it is more than 4.3 mm off the step centre.
STEP_WIDTH_MM = 16.0
END_WALL_MM = 3.0
BAR_DEPTH_MM = 12.0
APRON_DEPTH_MM = 22.0
FLOOR_MM = 1.6
LIP_GAP_MM = 1.4
LIP_THICKNESS_MM = 1.2


def make_ladder() -> cq.Shape:
    length = len(STEPS_MM) * STEP_WIDTH_MM + 2 * END_WALL_MM
    top = FLOOR_MM + LIP_GAP_MM + LIP_THICKNESS_MM
    bar = (
        cq.Workplane("XY")
        .center(length / 2 - END_WALL_MM, BAR_DEPTH_MM / 2)
        .rect(length, BAR_DEPTH_MM)
        .extrude(top)
    )
    apron = (
        cq.Workplane("XY")
        .center(length / 2 - END_WALL_MM, -APRON_DEPTH_MM / 2)
        .rect(length, APRON_DEPTH_MM)
        .extrude(FLOOR_MM)
    )
    body = bar.union(apron)

    for index, depth in enumerate(STEPS_MM):
        groove = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_MM)
            .center((index + 0.5) * STEP_WIDTH_MM, depth / 2 - 0.5)
            .rect(STEP_WIDTH_MM, depth + 1.0)
            .extrude(LIP_GAP_MM)
        )
        body = body.cut(groove)

    for index, depth in enumerate(STEPS_MM):
        label = (
            cq.Workplane("XY")
            .workplane(offset=top)
            .center((index + 0.5) * STEP_WIDTH_MM, BAR_DEPTH_MM - 4.0)
            .text(f"{depth:.1f}", 4.0, 0.5, combine=True)
        )
        body = body.union(label)

    solid = body.val()
    if not solid.isValid() or len(solid.Solids()) != 1:
        raise RuntimeError("Lip ladder is not a single valid solid")
    return solid


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "build" / "boa-lip-ladder" / "boa-lip-ladder.stl",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(make_ladder(), str(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
