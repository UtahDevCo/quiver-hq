from __future__ import annotations

import argparse

import cadquery as cq

from .cells import CELLS
from .export import export_stl, export_svg
from .ribs import mouth, ribs

# Squeeze = nominal diameter minus the diameter the three rib tips touch.
# Row 1 is a slip fit at nominal, rows 2 and 3 grip harder.
SQUEEZES = (0.0, 0.2, 0.4)

BORE_DEPTH = 15.0
FLOOR = 1.5
WALL = 3.0             # between neighbouring bores
EDGE = 4.0
LABEL_STRIP = 7.0
LABEL_SIZE = 4.0
LABEL_DEPTH = 0.6
LABEL_BAR = 3.0         # labels sit on raised bars; the rest of the base is just the bore floor
RING_WALL = 2.0         # each bore stands in its own ring; neighbours fuse where they touch


def build_coupon() -> cq.Workplane:
    pitch_y = max(c.bore for c in CELLS) + WALL
    xs, x = [], EDGE
    for c in CELLS:
        xs.append(x + c.bore / 2.0)
        x += c.bore + WALL
    width = x - WALL + EDGE
    depth = LABEL_STRIP + len(SQUEEZES) * pitch_y - WALL + EDGE
    height = BORE_DEPTH + FLOOR
    ys = [LABEL_STRIP + pitch_y / 2.0 - WALL / 2.0 + i * pitch_y for i in range(len(SQUEEZES))]

    plate = cq.Workplane("XY").box(width, depth, FLOOR, centered=False).edges("|Z").fillet(2.0)
    strips = (
        cq.Workplane("XY").box(width, LABEL_STRIP, LABEL_BAR, centered=False)
        .union(cq.Workplane("XY").box(EDGE + 1.0, depth, LABEL_BAR, centered=False).translate((width - EDGE - 1.0, 0, 0)))
        .edges("|Z").fillet(1.0)
    )
    rings = [
        cq.Solid.makeCylinder(c.bore / 2.0 + RING_WALL, height, cq.Vector(cx, cy, 0))
        for c, cx in zip(CELLS, xs) for cy in ys
    ]
    body = plate.union(strips).union(cq.Workplane().add(cq.Compound.makeCompound(rings)))

    bores = [
        cq.Solid.makeCylinder(c.bore / 2.0, BORE_DEPTH + 1.0, cq.Vector(cx, cy, FLOOR))
        for c, cx in zip(CELLS, xs) for cy in ys
    ]
    body = body.cut(cq.Workplane().add(cq.Compound.makeCompound(bores)))

    mouths = [mouth(c, height, cx, cy) for c, cx in zip(CELLS, xs) for cy in ys]
    body = body.cut(cq.Workplane().add(cq.Compound.makeCompound(mouths)))

    rib_solids = [
        r for c, cx in zip(CELLS, xs) for squeeze, cy in zip(SQUEEZES, ys)
        for r in ribs(c, squeeze, height, cx, cy)
    ]
    body = body.union(cq.Workplane().add(cq.Compound.makeCompound(rib_solids)))

    top = cq.Workplane("XY").workplane(offset=LABEL_BAR)
    labels = None
    for c, cx in zip(CELLS, xs):
        text = top.center(cx, LABEL_STRIP / 2.0 + 0.5).text(
            c.name, LABEL_SIZE * (0.8 if len(c.name) > 3 else 1.0), -LABEL_DEPTH, combine=False, halign="center", valign="center")
        labels = text if labels is None else labels.union(text)
    for i, cy in enumerate(ys):
        text = top.center(width - EDGE / 2.0 - 0.2, cy).text(
            str(i + 1), 3.0, -LABEL_DEPTH, combine=False, halign="center", valign="center")
        labels = labels.union(text)
    return body.cut(labels)


def main() -> None:
    parser = argparse.ArgumentParser(description="Crush-rib fit coupon: one bore per cell size per squeeze level")
    parser.add_argument("--svg", action="store_true", help="also export an SVG preview")
    args = parser.parse_args()
    coupon = build_coupon()
    solids = len(coupon.val().Solids())
    bb = coupon.val().BoundingBox()
    print(f"coupon: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, {solids} solid(s)")
    if solids != 1:
        raise SystemExit("coupon fragmented into more than one solid")
    print(export_stl(coupon, "fit-coupon"))
    if args.svg:
        print(export_svg(coupon, "fit-coupon", direction=(-0.6, -1.0, 1.4)))
    for c in CELLS:
        tips = ", ".join(f"{c.diameter - s:.2f}" for s in SQUEEZES)
        print(f"  {c.name:>6}: bore {c.bore:.1f}, rib tips touch {tips} mm (rows 1-3)")


if __name__ == "__main__":
    main()
