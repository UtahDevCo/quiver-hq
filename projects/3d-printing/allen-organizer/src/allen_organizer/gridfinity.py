from __future__ import annotations

import cadquery as cq

# Gridfinity constants (mm), from the gridfinity-rebuilt reference spec.
GRID = 42.0
BASE_TOP = 41.5            # foot top square (per cell), 0.5 clearance in the cell
R_TOP = 3.75              # top corner radius
CH_TOP = 2.15            # upper 45-degree taper height
STRAIGHT = 1.8          # vertical wall section
CH_BOT = 0.8           # lower 45-degree chamfer height
FOOT_H = CH_TOP + STRAIGHT + CH_BOT  # 4.75

OUTER_CLEARANCE = 0.5    # bin outer = grid*n - 0.5


def _rrect(size: float, r: float) -> cq.Sketch:
    return cq.Sketch().rect(size, size).reset().vertices().fillet(r)


def _one_foot() -> cq.Workplane:
    """A single Gridfinity foot, top at z=0, tapering down to z=-FOOT_H."""
    top = _rrect(BASE_TOP, R_TOP)
    mid = _rrect(BASE_TOP - 2 * CH_TOP, R_TOP - CH_TOP)
    bot = _rrect(BASE_TOP - 2 * CH_TOP - 2 * CH_BOT, R_TOP - CH_TOP - CH_BOT)

    def at(sk: cq.Sketch, z: float) -> cq.Sketch:
        return sk.moved(cq.Location(cq.Vector(0, 0, z)))

    top_taper = cq.Workplane("XY").placeSketch(at(mid, -CH_TOP), at(top, 0.0)).loft()
    straight = cq.Workplane("XY").placeSketch(
        at(mid, -CH_TOP - STRAIGHT), at(mid, -CH_TOP)
    ).loft()
    bot_chamfer = cq.Workplane("XY").placeSketch(
        at(bot, -FOOT_H), at(mid, -CH_TOP - STRAIGHT)
    ).loft()
    return top_taper.union(straight).union(bot_chamfer)


def cell_centers(nx: int, ny: int) -> list[tuple[float, float]]:
    x0 = -(nx - 1) * GRID / 2.0
    y0 = -(ny - 1) * GRID / 2.0
    return [(x0 + i * GRID, y0 + j * GRID) for j in range(ny) for i in range(nx)]


def base(nx: int, ny: int) -> cq.Workplane:
    """The Gridfinity foot array for an nx by ny bin. Foot tops at z=0."""
    feet = cq.Workplane("XY")
    for cx, cy in cell_centers(nx, ny):
        feet = feet.union(_one_foot().translate((cx, cy, 0)))
    return feet


def outer_dims(nx: int, ny: int) -> tuple[float, float]:
    return nx * GRID - OUTER_CLEARANCE, ny * GRID - OUTER_CLEARANCE


def body_slab(nx: int, ny: int, height: float) -> cq.Workplane:
    """The continuous bin body above the feet, from z=0 up to `height`."""
    w, d = outer_dims(nx, ny)
    return (
        cq.Workplane("XY")
        .sketch()
        .rect(w, d)
        .reset()
        .vertices()
        .fillet(R_TOP)
        .finalize()
        .extrude(height)
    )
