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

# Baseplate socket profile, bottom to top: 0.7 chamfer, 1.8 straight, 2.15 taper.
BP_CH_BOT = 0.7
BP_H = BP_CH_BOT + STRAIGHT + CH_TOP  # 4.65
BP_R = 4.0
BP_OVERLAP = 0.02        # neighbouring cell cutters overlap so no coincident faces


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


def bin_shell(nx: int, ny: int, total_h: float) -> cq.Workplane:
    """Solid bin: feet below z=0, body up to total_h - FOOT_H. Total height from foot bottom."""
    return base(nx, ny).union(body_slab(nx, ny, total_h - FOOT_H))


def _socket_cutter() -> cq.Workplane:
    """One open-bottom baseplate cell, bottom of the plate at z=0."""
    top_size = GRID + BP_OVERLAP
    mid_size = GRID - 2 * CH_TOP
    bot_size = mid_size - 2 * BP_CH_BOT
    top = rrect(top_size, top_size, BP_R)
    mid = rrect(mid_size, mid_size, BP_R - CH_TOP)
    bot = rrect(bot_size, bot_size, BP_R - CH_TOP - BP_CH_BOT)
    z_mid = BP_CH_BOT + STRAIGHT
    return (
        _loft(mid, z_mid, top, BP_H)
        .union(_loft(top, BP_H, top, BP_H + 1.0))
        .union(_loft(mid, BP_CH_BOT, mid, z_mid))
        .union(_loft(bot, 0.0, mid, BP_CH_BOT))
        .union(_loft(bot, -1.0, bot, 0.0))
    )


def baseplate(nx: int, ny: int, pad_x: float = 0.0, pad_y: float = 0.0) -> cq.Workplane:
    """Open-frame baseplate, nx by ny cells, with optional solid padding on the sides."""
    w = nx * GRID + 2 * pad_x
    d = ny * GRID + 2 * pad_y
    plate = cq.Workplane("XY").placeSketch(rrect(w, d, BP_R)).extrude(BP_H)
    cutter = _socket_cutter()
    for cx, cy in cell_centers(nx, ny):
        plate = plate.cut(cutter.translate((cx, cy, 0)))
    return plate
