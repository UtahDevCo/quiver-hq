from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

import cadquery as cq

from . import gridfinity as gf
from .cells import BY_NAME, Cell
from .export import export_stl, export_svg
from .ribs import mouth, ribs

# Drawer pose: big feet down at z<0, bore mouths up on the face at z=THICK.
# Shelf pose: stood on the -Y edge feet, face out, leaning back so bores run downhill.
NX, NY = 4, 2
WIDTH, HEIGHT = gf.outer_dims(NX, NY)       # 167.5 x 83.5
THICK = gf.BASE_TOP                         # 41.5, one unit, so the edge carries 4x1 feet
CORNER_R = 0.5         # small, or the end receivers break through the rounded corners
SIDE_WALL = 3.0
BORE_WALL = 2.0
MARGIN_BOTTOM = 4.0    # edge feet are outside the body, so the bottom row can sit close
MARGIN_TOP = 5.5       # clears the receiver pockets cut into the top edge
LANE_DEPTH = 10.0
LANE_WALL = 1.2        # left between a finger lane and the bores beside it
POCKET_WALL = 1.2


@dataclass(frozen=True)
class Brick:
    name: str
    rows: tuple[str, ...]   # bottom (edge-feet side) to top


BRICKS = (
    Brick("brick-aa", ("AA", "AA", "AA")),
    Brick("brick-18650", ("18650", "18650", "AAA")),
    Brick("brick-21700", ("21700", "21700", "AAA")),
)


def row_centers(cells: list[Cell]) -> tuple[list[float], float]:
    holes = sum(c.bore for c in cells)
    gap = (HEIGHT - MARGIN_BOTTOM - MARGIN_TOP - holes) / (len(cells) - 1)
    y, ys = -HEIGHT / 2.0 + MARGIN_BOTTOM, []
    for c in cells:
        ys.append(y + c.bore / 2.0)
        y += c.bore + gap
    return ys, gap


def column_centers(cell: Cell) -> list[float]:
    pitch = cell.bore + BORE_WALL
    n = math.floor((WIDTH - 2 * SIDE_WALL + BORE_WALL) / pitch)
    return [(i - (n - 1) / 2.0) * pitch for i in range(n)]


def _compound(solids: list[cq.Solid]) -> cq.Workplane:
    return cq.Workplane().add(cq.Compound.makeCompound(solids))


def _edge_feature(shape: cq.Workplane, x: float, y: float) -> cq.Solid:
    """Turn a Z-pointing foot or pocket so it points along -Y, centred on the brick's thickness."""
    return shape.rotate((0, 0, 0), (1, 0, 0), -90).translate((x, y, THICK / 2.0)).val()


def build_brick(brick: Brick) -> cq.Workplane:
    cells = [BY_NAME[k] for k in brick.rows]
    ys, gap = row_centers(cells)
    if gap - 2 * LANE_WALL < 7.0:
        raise SystemExit(f"{brick.name}: finger lanes only {gap - 2 * LANE_WALL:.1f} mm")
    unit_xs = [gf.GRID * (i - (NX - 1) / 2.0) for i in range(NX)]

    body = (
        cq.Workplane("XY").sketch().rect(WIDTH, HEIGHT).reset().vertices().fillet(CORNER_R)
        .finalize().extrude(THICK)
    )
    body = body.union(gf.base(NX, NY))
    foot = gf._one_foot()
    body = body.union(_compound([_edge_feature(foot, x, -HEIGHT / 2.0) for x in unit_xs]))

    pocket = gf.stacking_pocket(POCKET_WALL, THICK)
    body = body.cut(_compound([_edge_feature(pocket, x, HEIGHT / 2.0) for x in unit_xs]))

    x0, span = -WIDTH / 2.0 + SIDE_WALL, WIDTH - 2 * SIDE_WALL
    lanes = []
    for (lo, c_lo), (hi, c_hi) in zip(zip(ys, cells), zip(ys[1:], cells[1:])):
        y0 = lo + c_lo.bore / 2.0 + LANE_WALL
        y1 = hi - c_hi.bore / 2.0 - LANE_WALL
        lanes.append(cq.Solid.makeBox(span, y1 - y0, LANE_DEPTH + 1.0, cq.Vector(x0, y0, THICK - LANE_DEPTH)))
    body = body.cut(_compound(lanes))

    holes = [(c, x, y) for c, y in zip(cells, ys) for x in column_centers(c)]
    body = body.cut(_compound([
        cq.Solid.makeCylinder(c.bore / 2.0, c.depth + 1.0, cq.Vector(x, y, THICK - c.depth))
        for c, x, y in holes
    ]))
    body = body.cut(_compound([mouth(c, THICK, x, y) for c, x, y in holes]))
    return body.union(_compound([r for c, x, y in holes for r in ribs(c, c.squeeze, THICK, x, y)]))


def summary(brick: Brick) -> str:
    cells = [BY_NAME[k] for k in brick.rows]
    _, gap = row_centers(cells)
    counts: dict[str, int] = {}
    for c in cells:
        counts[c.name] = counts.get(c.name, 0) + len(column_centers(c))
    held = ", ".join(f"{n} x {k}" for k, n in counts.items())
    stick = max(c.length - c.depth for c in cells)
    drawer = THICK + gf.FOOT_H + stick
    return f"{held}; lanes {gap - 2 * LANE_WALL:.1f} mm; top of cells {drawer:.1f} mm above the drawer floor"


def main() -> None:
    parser = argparse.ArgumentParser(description="Two-faced Gridfinity battery bricks")
    parser.add_argument("names", nargs="*", help="bricks to build (default: all)")
    parser.add_argument("--svg", action="store_true", help="also export an SVG preview")
    args = parser.parse_args()
    for brick in BRICKS:
        if args.names and brick.name not in args.names:
            continue
        shape = build_brick(brick)
        solids = len(shape.val().Solids())
        bb = shape.val().BoundingBox()
        print(f"{brick.name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, "
              f"{shape.val().Volume() / 1000:.0f} cm³, {solids} solid(s)")
        print(f"  {summary(brick)}")
        if solids != 1:
            raise SystemExit(f"{brick.name} fragmented into {solids} solids")
        print(f"  {export_stl(shape, brick.name)}")
        if args.svg:
            print(f"  {export_svg(shape, brick.name, direction=(-0.6, -1.0, 1.4))}")


if __name__ == "__main__":
    main()
