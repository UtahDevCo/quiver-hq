from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

import cadquery as cq

from . import gridfinity as gf
from .cells import BY_NAME, Hole
from .export import export_stl, export_svg
from .holes import chamfer, cutter, grip, opening, wall

# Drawer pose: big feet down at z<0, hole mouths up on the face at z=THICK.
# Shelf pose: stood on the -Y edge feet, face out, leaning back so bores run downhill.
THICK = gf.BASE_TOP                         # 41.5, one unit, so the edge carries Nx1 feet
CORNER_R = 0.5         # small, or the end receivers break through the rounded corners
SIDE_WALL = 3.0
MARGIN_BOTTOM = 4.0    # edge feet are outside the body, so the bottom row can sit close
MARGIN_TOP = 5.5       # clears the receiver pockets cut into the top edge
LANE_DEPTH = 10.0
LANE_WALL = 1.2        # left between a finger lane and the holes beside it
LANE_MIN = 7.0
POCKET_WALL = 1.2
STACK_GAP = gf.FOOT_H - gf.stacking_pocket_depth(POCKET_WALL, THICK)   # body to body when stacked

Row = tuple[tuple[str, int | None], ...]   # (hole, count) left to right; None fills the row


def fill(name: str) -> Row:
    return ((name, None),)


@dataclass(frozen=True)
class Brick:
    name: str
    nx: int
    ny: int
    rows: tuple[Row, ...]   # bottom (edge-feet side) to top

    @property
    def width(self) -> float:
        return gf.outer_dims(self.nx, self.ny)[0]

    @property
    def height(self) -> float:
        return gf.outer_dims(self.nx, self.ny)[1]


# 4 wide: the AA and 18650 bricks were printed at this width on 2026-11-04/05.
BRICKS = (
    Brick("brick-aa", 4, 2, (fill("AA"), fill("AA"), fill("AA"))),
    Brick("brick-18650", 4, 2, (fill("18650"), fill("18650"), fill("AAA"))),
    Brick("brick-21700", 4, 2, (fill("21700"), fill("AA"), fill("AAA"))),
    Brick("brick-odds", 4, 1, ((("C", 2), ("9V", 3), ("coin", 8)),)),
)


def _compound(solids: list[cq.Solid]) -> cq.Workplane:
    return cq.Workplane().add(cq.Compound.makeCompound(solids))


def resolve(brick: Brick, row: Row) -> list[tuple[Hole, int]]:
    span = brick.width - 2 * SIDE_WALL
    out = []
    for name, n in row:
        hole = BY_NAME[name]
        if n is None:
            n = math.floor((span + wall(hole)) / (opening(hole)[0] + wall(hole)))
        out.append((hole, n))
    return out


def row_height(row: list[tuple[Hole, int]]) -> float:
    return max(opening(h)[1] for h, _ in row)


def row_centers(brick: Brick) -> tuple[list[float], float]:
    rows = [resolve(brick, r) for r in brick.rows]
    heights = [row_height(r) for r in rows]
    room = brick.height - MARGIN_BOTTOM - MARGIN_TOP - sum(heights)
    if len(rows) == 1:
        return [-brick.height / 2.0 + MARGIN_BOTTOM + room / 2.0 + heights[0] / 2.0], 0.0
    gap = room / (len(rows) - 1)
    y, ys = -brick.height / 2.0 + MARGIN_BOTTOM, []
    for h in heights:
        ys.append(y + h / 2.0)
        y += h + gap
    return ys, gap


def hole_positions(brick: Brick, row: list[tuple[Hole, int]]) -> list[tuple[Hole, float]]:
    total = sum(n * (opening(h)[0] + wall(h)) for h, n in row) - wall(row[-1][0])
    if total > brick.width - 2 * SIDE_WALL:
        raise SystemExit(f"{brick.name}: row is {total:.1f} mm, wider than the brick")
    x, out = -total / 2.0, []
    for h, n in row:
        w = opening(h)[0]
        for _ in range(n):
            out.append((h, x + w / 2.0))
            x += w + wall(h)
    return out


def build_brick(brick: Brick) -> cq.Workplane:
    rows = [resolve(brick, r) for r in brick.rows]
    ys, gap = row_centers(brick)
    if len(rows) > 1 and gap - 2 * LANE_WALL < LANE_MIN:
        raise SystemExit(f"{brick.name}: finger lanes only {gap - 2 * LANE_WALL:.1f} mm")
    unit_xs = [gf.GRID * (i - (brick.nx - 1) / 2.0) for i in range(brick.nx)]

    body = (
        cq.Workplane("XY").sketch().rect(brick.width, brick.height).reset().vertices().fillet(CORNER_R)
        .finalize().extrude(THICK)
    )
    body = body.union(gf.base(brick.nx, brick.ny))
    foot = gf._one_foot()
    body = body.union(_compound([_edge_feature(foot, x, -brick.height / 2.0) for x in unit_xs]))
    pocket = gf.stacking_pocket(POCKET_WALL, THICK)
    body = body.cut(_compound([_edge_feature(pocket, x, brick.height / 2.0) for x in unit_xs]))

    x0, span = -brick.width / 2.0 + SIDE_WALL, brick.width - 2 * SIDE_WALL
    lanes = []
    for lo, hi, r_lo, r_hi in zip(ys, ys[1:], rows, rows[1:]):
        y0 = lo + row_height(r_lo) / 2.0 + LANE_WALL
        y1 = hi - row_height(r_hi) / 2.0 - LANE_WALL
        lanes.append(cq.Solid.makeBox(span, y1 - y0, LANE_DEPTH + 1.0, cq.Vector(x0, y0, THICK - LANE_DEPTH)))
    if lanes:
        body = body.cut(_compound(lanes))

    holes = [(h, x, y) for r, y in zip(rows, ys) for h, x in hole_positions(brick, r)]
    body = body.cut(_compound([cutter(h, THICK, x, y) for h, x, y in holes]))
    mouths = [m for h, x, y in holes if (m := chamfer(h, THICK, x, y)) is not None]
    body = body.cut(_compound(mouths))
    return body.union(_compound([r for h, x, y in holes for r in grip(h, THICK, x, y)]))


def _edge_feature(shape: cq.Workplane, x: float, y: float) -> cq.Solid:
    """Turn a Z-pointing foot or pocket so it points along -Y, centred on the brick's thickness."""
    return shape.rotate((0, 0, 0), (1, 0, 0), -90).translate((x, y, THICK / 2.0)).val()


def summary(brick: Brick) -> str:
    rows = [resolve(brick, r) for r in brick.rows]
    _, gap = row_centers(brick)
    counts: dict[str, int] = {}
    for row in rows:
        for h, n in row:
            counts[h.name] = counts.get(h.name, 0) + n
    held = ", ".join(f"{n} x {k}" for k, n in counts.items())
    stick = max(h.length - h.depth for row in rows for h, _ in row)
    lanes = f"lanes {gap - 2 * LANE_WALL:.1f} mm; " if len(rows) > 1 else ""
    return f"{held}; {lanes}top of cells {THICK + gf.FOOT_H + stick:.1f} mm above the drawer floor"


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
