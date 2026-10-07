"""Print-in-place brace hinge coupon: two short segments joined by one hinge.

The brace is meant to print as one chain of rigid segments joined by vertical
print-in-place hinges, so it can never fall apart.  Each hinge is a stack of
interleaved knuckles with 45 degree cone pivots between them, which print
without support and trap each knuckle vertically.

The hinge axis sits just inside the outer surface.  Opening the chain (bending
outward, for putting it on) is free; closing it is stopped by the inner end
faces meeting at the designed ring shape, so every joint is a hard
minimum-circumference stop.  The segments print opened by STOP_WEDGE_DEG so
the stop faces are separated by a printable gap, and they close flush.

Coupon geometry uses a circular ring; the real brace follows the sleeve's
smoothed outer envelope.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq

from .config import PROJECT_ROOT


INNER_RADIUS_MM = 52.0
WALL_MM = 8.0
HEIGHT_MM = 36.0
SEGMENT_SPAN_DEG = 30.0
JOINT_ANGLE_DEG = 90.0

KNUCKLE_RADIUS_MM = 3.5
AXIS_INSET_MM = 1.25  # hinge axis this far inside the outer surface
CONE_RADIUS_MM = 3.1
CLEARANCE_MM = 0.35
KNUCKLE_BANDS = 5  # owners alternate A, B, A, B, A from the bottom
STOP_WEDGE_DEG = 4.5  # print-time opening; ~0.30 mm to 0.53 mm stop-face gap

OUTER_RADIUS_MM = INNER_RADIUS_MM + WALL_MM


def _axis_point() -> tuple[float, float]:
    r = OUTER_RADIUS_MM - AXIS_INSET_MM
    a = math.radians(JOINT_ANGLE_DEG)
    return r * math.cos(a), r * math.sin(a)


def _sector(start_deg: float, end_deg: float) -> cq.Workplane:
    ring = (
        cq.Workplane("XY")
        .circle(OUTER_RADIUS_MM)
        .circle(INNER_RADIUS_MM)
        .extrude(HEIGHT_MM)
    )
    far = OUTER_RADIUS_MM * 3
    steps = max(2, int(abs(end_deg - start_deg) // 5) + 1)
    points = [(0.0, 0.0)] + [
        (
            far * math.cos(math.radians(start_deg + (end_deg - start_deg) * i / steps)),
            far * math.sin(math.radians(start_deg + (end_deg - start_deg) * i / steps)),
        )
        for i in range(steps + 1)
    ]
    wedge = cq.Workplane("XY").polyline(points).close().extrude(HEIGHT_MM)
    return ring.intersect(wedge)


def _cylinder(radius: float, z0: float, z1: float) -> cq.Workplane:
    x, y = _axis_point()
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(radius).extrude(z1 - z0)


CONE_TIP_RADIUS_MM = 0.4  # flat tip; a sharp apex tessellates badly


def _cone(base_radius: float, base_z: float) -> cq.Workplane:
    """Upward 45 degree cone frustum with its base at base_z, on the hinge axis."""
    x, y = _axis_point()
    height = base_radius - CONE_TIP_RADIUS_MM
    return cq.Workplane("XY").add(
        cq.Solid.makeCone(base_radius, CONE_TIP_RADIUS_MM, height, cq.Vector(x, y, base_z))
    )


def _band_edges() -> list[float]:
    return [HEIGHT_MM * i / KNUCKLE_BANDS for i in range(KNUCKLE_BANDS + 1)]


def _build_pair() -> tuple[cq.Shape, cq.Shape]:
    """Return segments A and B in the closed (target) pose."""
    half_gap = CLEARANCE_MM / 2
    edges = _band_edges()
    bodies = {
        "A": _sector(JOINT_ANGLE_DEG - SEGMENT_SPAN_DEG, JOINT_ANGLE_DEG),
        "B": _sector(JOINT_ANGLE_DEG, JOINT_ANGLE_DEG + SEGMENT_SPAN_DEG),
    }
    owners = ["A" if i % 2 == 0 else "B" for i in range(KNUCKLE_BANDS)]

    for i, owner in enumerate(owners):
        other = "B" if owner == "A" else "A"
        z0 = edges[i] - (half_gap if i > 0 else 0.0)
        z1 = edges[i + 1] + (half_gap if i < KNUCKLE_BANDS - 1 else 0.0)
        bodies[other] = bodies[other].cut(
            _cylinder(KNUCKLE_RADIUS_MM + CLEARANCE_MM, z0 - 0.01, z1 + 0.01)
        )

    for i, owner in enumerate(owners):
        z0 = edges[i] + (half_gap if i > 0 else 0.0)
        z1 = edges[i + 1] - (half_gap if i < KNUCKLE_BANDS - 1 else 0.0)
        knuckle = _cylinder(KNUCKLE_RADIUS_MM, z0, z1)
        if i < KNUCKLE_BANDS - 1:
            knuckle = knuckle.union(_cone(CONE_RADIUS_MM, z1))
        bodies[owner] = bodies[owner].union(knuckle)

    for i, owner in enumerate(owners):
        if i == 0:
            continue
        recess = _cone(CONE_RADIUS_MM + CLEARANCE_MM * math.sqrt(2), edges[i] - half_gap)
        bodies[owner] = bodies[owner].cut(recess)

    return bodies["A"].val(), bodies["B"].val()


def _rotate_about_axis(shape: cq.Shape, degrees: float) -> cq.Shape:
    x, y = _axis_point()
    return shape.rotate(cq.Vector(x, y, 0), cq.Vector(x, y, 1), degrees)


def make_coupon() -> tuple[cq.Shape, cq.Shape]:
    """Segments in the print pose: B opened by STOP_WEDGE_DEG (clockwise)."""
    a, b = _build_pair()
    return a, _rotate_about_axis(b, -STOP_WEDGE_DEG)


def check(a: cq.Shape, b_print: cq.Shape) -> dict:
    """Clearance at print pose, flush closure, stop, and opening range."""

    def overlap(extra_open_deg: float) -> float:
        moved = _rotate_about_axis(b_print, -extra_open_deg)
        return a.intersect(moved).Volume()

    result = {
        "print_pose_min_gap_mm": round(a.distance(b_print), 3),
        "overlap_at_closed_mm3": round(overlap(-STOP_WEDGE_DEG), 3),
        "overlap_1deg_past_closed_mm3": round(overlap(-STOP_WEDGE_DEG - 1.0), 3),
    }
    free = 0.0
    for degrees in range(5, 181, 5):
        if overlap(degrees - STOP_WEDGE_DEG) > 0.01:
            break
        free = float(degrees)
    result["free_opening_beyond_closed_deg"] = free
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "build" / "hinge-coupon")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    a, b = make_coupon()
    for shape in (a, b):
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise RuntimeError("Hinge segment is not a single valid solid")
    cq.exporters.export(cq.Compound.makeCompound([a, b]), str(args.output_dir / "hinge-coupon-v1.stl"))
    report = check(a, b)
    (args.output_dir / "hinge-coupon-v1.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
