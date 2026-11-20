from __future__ import annotations

import cadquery as cq

# A rounded-square bucket, a lid ring that drops over its rim, and a flap that swings on two
# pins across the middle of the ring. A weight under the flap's axis pulls it back level.
# Parts are modelled in use orientation (z up); the *_print functions turn them for the bed.

BODY_W = 140.0
BODY_H = 100.3           # 4.5 in overall with the lid on
BODY_R = 30.0            # vertical corner radius
BODY_WALL = 2.0
BODY_FLOOR = 2.4
BODY_FOOT_FILLET = 4.0

LID_CLEARANCE = 0.4      # per side, skirt over the body
LID_SKIRT_WALL = 2.0
LID_SKIRT_H = 12.0       # how far the ring hangs over the body
LID_TOP_H = 14.0         # ring above the rim, where the flap pivots
LID_OPENING = 132.0      # 2 mm inside the body's inner wall, so the rim is hidden

FLAP_GAP = 2.0           # per side, flap to opening
FLAP_T = 2.0
FLAP_RECESS = 2.0        # flap top below the lid top when closed
AXIS_BELOW_FLAP_TOP = 3.5
HUB_D = 10.0
HUB_L = 12.0
KEEL_X = 26.0            # along the axis
KEEL_Y = 14.0
KEEL_DEPTH = 58.0        # below the axis

PIN_D = 4.0
PIN_HOLE_D = 4.4         # pin turns in the lid
PIN_BORE_D = 3.9         # pin presses into the flap
PIN_BORE_DEPTH = 9.0
PIN_HEAD_D = 8.0
PIN_HEAD_T = 1.6
PIN_FLAT = 1.6           # flat cut below the axis so the pin prints lying down

LID_OUTER = BODY_W + 2 * (LID_CLEARANCE + LID_SKIRT_WALL)
LID_H = LID_SKIRT_H + LID_TOP_H
AXIS_Z = LID_H - FLAP_RECESS - AXIS_BELOW_FLAP_TOP   # in the lid's frame, lid bottom at 0
FLAP_W = LID_OPENING - 2 * FLAP_GAP
LID_WALL_AT_PIN = (LID_OUTER - LID_OPENING) / 2
PIN_L = LID_WALL_AT_PIN + FLAP_GAP + PIN_BORE_DEPTH - 0.5


def _rounded_block(w: float, r: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .rect(w, w)
        .extrude(z1 - z0)
        .edges("|Z")
        .fillet(r)
        .translate((0, 0, z0))
    )


def body() -> cq.Workplane:
    inner_w = BODY_W - 2 * BODY_WALL
    shell = _rounded_block(BODY_W, BODY_R, 0, BODY_H).faces("<Z").edges().fillet(BODY_FOOT_FILLET)
    return shell.cut(_rounded_block(inner_w, BODY_R - BODY_WALL, BODY_FLOOR, BODY_H + 1))


def lid() -> cq.Workplane:
    lid_r = BODY_R + LID_CLEARANCE + LID_SKIRT_WALL
    opening_r = BODY_R - (BODY_W - LID_OPENING) / 2
    skirt_w = BODY_W + 2 * LID_CLEARANCE
    ring = (
        _rounded_block(LID_OUTER, lid_r, 0, LID_H)
        .cut(_rounded_block(skirt_w, BODY_R + LID_CLEARANCE, -1, LID_SKIRT_H))
        .cut(_rounded_block(LID_OPENING, opening_r, -1, LID_H + 1))
    )
    pin_holes = (
        cq.Workplane("YZ")
        .circle(PIN_HOLE_D / 2)
        .extrude(LID_OUTER + 2)
        .translate((-LID_OUTER / 2 - 1, 0, AXIS_Z))
    )
    return ring.cut(pin_holes)


def flap() -> cq.Workplane:
    """Axis along x through the origin."""
    flap_r = BODY_R - (BODY_W - LID_OPENING) / 2 - FLAP_GAP
    top = AXIS_BELOW_FLAP_TOP
    plate = _rounded_block(FLAP_W, flap_r, top - FLAP_T, top)
    hubs = (
        cq.Workplane("YZ")
        .circle(HUB_D / 2)
        .extrude(FLAP_W)
        .translate((-FLAP_W / 2, 0, 0))
        .cut(cq.Workplane("XY").box(FLAP_W - 2 * HUB_L, HUB_D + 2, HUB_D + 2))
        .cut(cq.Workplane("XY").box(FLAP_W + 2, HUB_D + 2, HUB_D).translate((0, 0, top + HUB_D / 2)))
    )
    keel = (
        cq.Workplane("XY")
        .box(KEEL_X, KEEL_Y, KEEL_DEPTH + top - FLAP_T, centered=(True, True, False))
        .translate((0, 0, -KEEL_DEPTH))
        .edges("|Z or <Z")
        .fillet(KEEL_Y / 2 - 0.5)
    )
    bores = (
        cq.Workplane("YZ")
        .circle(PIN_BORE_D / 2)
        .extrude(PIN_BORE_DEPTH)
        .translate((FLAP_W / 2 - PIN_BORE_DEPTH, 0, 0))
    )
    bores = bores.union(bores.mirror("YZ"))
    return plate.union(hubs).union(keel).cut(bores)


def pin() -> cq.Workplane:
    """Axis along x, head at x = 0, shaft toward +x."""
    head = cq.Workplane("YZ").circle(PIN_HEAD_D / 2).extrude(PIN_HEAD_T)
    shaft = cq.Workplane("YZ").circle(PIN_D / 2).extrude(PIN_L).translate((PIN_HEAD_T, 0, 0))
    tip = shaft.faces(">X").edges().chamfer(0.4)
    flat = cq.Workplane("XY").box(PIN_L + 10, PIN_HEAD_D + 2, PIN_HEAD_D).translate(
        (PIN_L / 2, 0, -PIN_FLAT - PIN_HEAD_D / 2)
    )
    return head.union(tip).cut(flat)


def lid_print() -> cq.Workplane:
    """Upside down: the top face goes on the bed and the skirt prints on the thicker upper wall."""
    return lid().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, LID_H))


def flap_print() -> cq.Workplane:
    """Top face on the bed, keel and hubs up."""
    return flap().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, AXIS_BELOW_FLAP_TOP))


def pin_print() -> cq.Workplane:
    """Two pins lying on their flats."""
    one = pin().translate((0, 0, PIN_FLAT))
    return one.union(one.translate((0, PIN_HEAD_D + 4, 0)))


def assembly() -> cq.Workplane:
    """Everything in place, for a look in a viewer. Not for printing."""
    lid_z = BODY_H - LID_SKIRT_H
    axis = (0, 0, lid_z + AXIS_Z)
    pin_x = LID_OUTER / 2 + PIN_HEAD_T
    east = pin().rotate((0, 0, 0), (0, 0, 1), 180).translate((pin_x, 0, 0))
    west = pin().translate((-pin_x, 0, 0))
    return (
        body()
        .union(lid().translate((0, 0, lid_z)))
        .union(flap().translate(axis))
        .union(east.translate(axis))
        .union(west.translate(axis))
    )
