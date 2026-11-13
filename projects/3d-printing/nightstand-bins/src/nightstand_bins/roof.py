from __future__ import annotations

import math

import cadquery as cq

from . import gridfinity as gf

# Roof 3c: a 2 x 5 slot block down the left edge, the side facing the bed. x runs left to
# right, y front to back. Both device slots lean right, so the screens tip toward the bed.
LEAN_DEG = 10.0
SLOT_DEPTH = 28.0
SIDE_WALL = 2.5
END_WALL = 2.5
DIVIDER = 3.0
PHONE_SLOT = 17.0        # 15 mm phone in its case + 2
IPAD_SLOT = 16.0         # 14 mm iPad in its case + 2

# Cable catch: a 5 mm slot open to the back and the top, under a pocket the plug's
# 12 x 6.5 mm molded head parks in. The 4 mm cable slides; the head can't follow.
CATCH_SLOT = 5.0
POCKET_W = 13.0          # along the back edge
POCKET_D = 7.5           # front to back
POCKET_DEPTH = 8.0
POCKET_BACK_WALL = 1.75
RAIL_DEPTH = 12.5
CATCH_XS = (12.0, 30.0)  # from the block's centre line, behind the channel
# The roof runs about 10 mm past the bin's back edge, so the catches sit on a ledge that hangs
# half a cell off the back and the cable drops clear of the roof. The ledge's underside rises
# at 45 degrees so it prints without support.
CATCH_OVERHANG = 21.0
LEDGE_TIP_THICKNESS = 12.0
LEDGE_SIDE_WALL = 2.0

WATCH_SLOT = 5.0


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def _leaning_slot(x_bottom: float, width: float, z_floor: float, z_top: float,
                  y0: float, y1: float) -> cq.Workplane:
    """A slot whose walls lean right by LEAN_DEG, `width` wide measured across x."""
    shift = (z_top - z_floor) * math.tan(math.radians(LEAN_DEG))
    pts = [
        (x_bottom, z_floor),
        (x_bottom + width, z_floor),
        (x_bottom + width + shift, z_top),
        (x_bottom + shift, z_top),
    ]
    prism = cq.Workplane("XZ").polyline(pts).close().extrude(400, both=True)
    return prism.intersect(_box(-200, 200, y0, y1, -50, 200))


def _ledge(x0: float, x1: float, y0: float, y1: float, z_top: float) -> cq.Workplane:
    """A shelf off the back face, LEDGE_TIP_THICKNESS thick at y1, its underside at 45 degrees."""
    z_tip = z_top - LEDGE_TIP_THICKNESS
    z_root = z_tip - (y1 - y0)
    pts = [(y0, z_root), (y1, z_tip), (y1, z_top), (y0, z_top)]
    return cq.Workplane("YZ").polyline(pts).close().extrude(x1 - x0).translate((x0, 0, 0))


def slot_block(ny: int = 5) -> cq.Workplane:
    """The 2 x ny slot block. ny=1 is the fit test: the back cell, with both slots and catches."""
    w, d = gf.outer_dims(2, ny)
    z_top = 6 * gf.U - gf.FOOT_H
    z_floor = z_top - SLOT_DEPTH
    above = z_top + 1.0
    left, right = -w / 2, w / 2
    front, back = -d / 2, d / 2
    inner_back = back - END_WALL
    inner_front = front + END_WALL

    phone_x = left + SIDE_WALL
    ipad_x = phone_x + PHONE_SLOT + DIVIDER
    channel_x = ipad_x + IPAD_SLOT + SIDE_WALL

    body = gf.base(2, ny).union(gf.body_slab(2, ny, z_top))
    phone = _leaning_slot(phone_x, PHONE_SLOT, z_floor, above, inner_front, inner_back)
    ipad = _leaning_slot(ipad_x, IPAD_SLOT, z_floor, above, front - 5.0, inner_back)
    channel = _leaning_slot(channel_x, 200.0, z_floor, above, inner_front, back - RAIL_DEPTH)
    channel = channel.intersect(_box(-200, right - SIDE_WALL, -200, 200, -50, 200))
    block = body.cut(phone).cut(ipad).cut(channel)

    tip = back + CATCH_OVERHANG
    ledge_x0 = min(CATCH_XS) - POCKET_W / 2 - LEDGE_SIDE_WALL
    ledge_x1 = max(CATCH_XS) + POCKET_W / 2 + LEDGE_SIDE_WALL
    block = block.union(_ledge(ledge_x0, ledge_x1, back - 1.0, tip, z_top))

    pocket_y1 = tip - POCKET_BACK_WALL
    pocket_y0 = pocket_y1 - POCKET_D
    cable_y = (pocket_y0 + pocket_y1) / 2
    for x in CATCH_XS:
        pocket = _box(x - POCKET_W / 2, x + POCKET_W / 2, pocket_y0, pocket_y1, z_top - POCKET_DEPTH, above)
        slot = _box(x - CATCH_SLOT / 2, x + CATCH_SLOT / 2, cable_y - CATCH_SLOT / 2, tip + 1.0, -gf.FOOT_H - 1.0, above)
        block = block.cut(pocket.edges("|Z").fillet(1.5)).cut(slot)
    return block


def watch_dish() -> cq.Workplane:
    """Dish A: an open 2 x 2 dish, 3u, with a cable slot in the back wall down to the floor."""
    dish = gf.open_tray(2, 2, 3)
    _, d = gf.outer_dims(2, 2)
    floor = 1.0
    slot = _box(-WATCH_SLOT / 2, WATCH_SLOT / 2, d / 2 - 5.0, d / 2 + 1.0, floor, 40.0)
    return dish.cut(slot)
