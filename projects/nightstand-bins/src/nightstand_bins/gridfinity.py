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

# Stacking lip, gridfinity-rebuilt profile, top to bottom: 1.9 taper, 1.8 straight, 0.7 taper.
# Its straight section is 37.7 wide per cell, the same as a baseplate socket, so a foot
# stacked on the lip seats the way it seats in a baseplate.
LIP_TOP = 1.9
LIP_STRAIGHT = 1.8
LIP_BOT = 0.7
LIP_H = LIP_TOP + LIP_STRAIGHT + LIP_BOT  # 4.4
LIP_RIM = 0.4            # flat left on top of the lip instead of a knife edge
U = 7.0                  # one Gridfinity height unit


def rrect(w: float, d: float, r: float) -> cq.Sketch:
    return cq.Sketch().rect(w, d).reset().vertices().fillet(r)


def _at(sk: cq.Sketch, z: float) -> cq.Sketch:
    return sk.moved(cq.Location(cq.Vector(0, 0, z)))


def _loft(lo: cq.Sketch, z_lo: float, hi: cq.Sketch, z_hi: float) -> cq.Workplane:
    return cq.Workplane("XY").placeSketch(_at(lo, z_lo), _at(hi, z_hi)).loft()


def _one_foot() -> cq.Workplane:
    """A single Gridfinity foot, top at z=0, tapering down to z=-FOOT_H."""
    top = rrect(BASE_TOP, BASE_TOP, R_TOP)
    mid_size = BASE_TOP - 2 * CH_TOP
    mid = rrect(mid_size, mid_size, R_TOP - CH_TOP)
    bot_size = mid_size - 2 * CH_BOT
    bot = rrect(bot_size, bot_size, R_TOP - CH_TOP - CH_BOT)
    return (
        _loft(mid, -CH_TOP, top, 0.0)
        .union(_loft(mid, -CH_TOP - STRAIGHT, mid, -CH_TOP))
        .union(_loft(bot, -FOOT_H, mid, -CH_TOP - STRAIGHT))
    )


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
    return cq.Workplane("XY").placeSketch(rrect(w, d, R_TOP)).extrude(height)


def lip_cutter(nx: int, ny: int, wall: float, z0: float) -> cq.Workplane:
    """The stacking-lip hollow above a bin wall that ends at z0, plus the 45-degree
    support that carries the lip's overhang back out to the inner wall."""
    w, d = outer_dims(nx, ny)

    def ring(inset: float) -> cq.Sketch:
        return rrect(w - 2 * inset, d - 2 * inset, R_TOP - inset)

    straight_inset = LIP_TOP
    bot_inset = LIP_TOP + LIP_BOT
    z_straight_top = z0 + LIP_BOT + LIP_STRAIGHT
    return (
        _loft(ring(straight_inset), z_straight_top, ring(LIP_RIM), z0 + LIP_H)
        .union(_loft(ring(LIP_RIM), z0 + LIP_H, ring(LIP_RIM), z0 + LIP_H + 1.0))
        .union(_loft(ring(straight_inset), z0 + LIP_BOT, ring(straight_inset), z_straight_top))
        .union(_loft(ring(bot_inset), z0, ring(straight_inset), z0 + LIP_BOT))
        .union(_loft(ring(wall), z0 - (bot_inset - wall), ring(bot_inset), z0))
    )


def open_tray(nx: int, ny: int, units: float, wall: float = 1.2, floor: float = 1.0,
              inner_fillet: float = 2.0) -> cq.Workplane:
    """An open bin `units` tall (7 mm each, foot bottom to wall top) with a stacking lip.

    Foot tops sit at z=0, the floor at z=floor, the wall top at units*U - FOOT_H.
    """
    w, d = outer_dims(nx, ny)
    z0 = units * U - FOOT_H
    body = base(nx, ny).union(body_slab(nx, ny, z0 + LIP_H))
    support_inset = LIP_TOP + LIP_BOT
    cavity_top = z0 - (support_inset - wall)
    cavity = (
        cq.Workplane("XY")
        .placeSketch(rrect(w - 2 * wall, d - 2 * wall, R_TOP - wall))
        .extrude(cavity_top - floor + 0.01)
        .edges("<Z")
        .fillet(inner_fillet)
        .translate((0, 0, floor))
    )
    return body.cut(cavity).cut(lip_cutter(nx, ny, wall, z0))
