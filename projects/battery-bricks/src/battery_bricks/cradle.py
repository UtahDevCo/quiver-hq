from __future__ import annotations

import argparse
import math

import cadquery as cq

from . import gridfinity as gf
from .brick import BRICKS, POCKET_WALL, STACK_GAP, THICK, _compound
from .export import export_stl

# Print pose and model frame: X across the shelf, Y = distance along the sloped board
# from its front edge toward the wall, Z = height off the board. The board meets a
# vertical wall, so in this frame the wall is the line y = SHELF_DEPTH - z * tan(angle).
SHELF_DEPTH = 177.8    # 7 in along the slope
SHELF_ANGLE = 18.0     # angle finder read 4 in of rise per 12 in
OPENING = 305.0        # 12 in clear above the board's front edge
STACK = ("brick-aa", "brick-18650", "brick-21700", "brick-odds")   # bottom to top
SPLIT_AFTER = 3        # the base piece stops at the top of the third brick; the Plus 4 prints 280 mm

BASE = 5.0             # slab under the bottom brick, holds its receivers
FACE_T = 2.4           # the lattice the bricks' drawer feet lean on
TOP_WEDGE = 4.0        # cradle depth left at the top of the stack, face included
FIN_T = 4.0            # free-standing back strips, so stiffer than the face
FIN_FRAME = 8.0
FLANGE = 12.0          # fin front edge widens to this, so each column of drawer feet has a pad
STRUT = 6.0
STRUT_PITCH = 60.0
LATTICE = 5.0
BACK_RAIL = 8.0
CORNER_CHAMFER = 4.0   # clears a bead of caulk where the board meets the wall
PEG = 5.0              # square pegs on the topper, one per column, into the base piece's flanges
PEG_LEN = 8.0
PEG_CLEAR = 0.2

TAN = math.tan(math.radians(SHELF_ANGLE))
_BRICKS = [next(b for b in BRICKS if b.name == n) for n in STACK]
NX = _BRICKS[0].nx
WIDTH = _BRICKS[0].width
LEVELS = [BASE + sum(b.height + STACK_GAP for b in _BRICKS[:i]) for i in range(len(_BRICKS) + 1)]
STACK_TOP = LEVELS[-1]
SPLIT = LEVELS[SPLIT_AFTER]
FACE_Y = SHELF_DEPTH - STACK_TOP * TAN - TOP_WEDGE   # where the drawer-feet tips touch
BRICK_FRONT = FACE_Y - THICK - gf.FOOT_H
COLUMNS = [gf.GRID * (i - (NX - 1) / 2.0) for i in range(NX)]


def wall_y(z: float) -> float:
    return SHELF_DEPTH - z * TAN


def _prism(points: list[tuple[float, float]], x0: float, width: float) -> cq.Workplane:
    """A (y, z) outline extruded across X from x0 to x0 + width."""
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(points).close().extrude(width)


def _bar(y: float, z: float, length: float, width: float, x0: float, span: float, angle: float) -> cq.Solid:
    """A strut in the YZ plane starting at (y, z), rising at `angle` degrees toward +Y."""
    box = cq.Solid.makeBox(span, length, width, cq.Vector(x0, 0, -width / 2.0))
    return box.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), angle).translate(cq.Vector(0, y, z))


def _fin(x: float) -> cq.Workplane:
    c = CORNER_CHAMFER
    outline = [(FACE_Y, 0.0), (SHELF_DEPTH - c, 0.0), (wall_y(c), c), (wall_y(STACK_TOP), STACK_TOP), (FACE_Y, STACK_TOP)]
    fin = _prism(outline, x - FIN_T / 2.0, FIN_T)

    front = FACE_Y + FIN_FRAME
    back_off = FIN_FRAME / math.cos(math.radians(SHELF_ANGLE))
    apex_z = (SHELF_DEPTH - back_off - front) / TAN
    window = _prism([(front, FIN_FRAME), (wall_y(FIN_FRAME) - back_off, FIN_FRAME), (front, apex_z)],
                    x - FIN_T, 2 * FIN_T)
    struts = [
        _bar(front, z, 200.0, STRUT, x - FIN_T, 2 * FIN_T, 45.0)
        for z in [FIN_FRAME + k * STRUT_PITCH for k in range(int(apex_z // STRUT_PITCH) + 1)]
    ]
    window = window.cut(_compound(struts))
    flange = cq.Workplane("XY").box(FLANGE, FIN_FRAME, STACK_TOP - BASE, centered=False).translate(
        (x - FLANGE / 2.0, FACE_Y, BASE))
    return fin.cut(window).union(flange)


def _lattice() -> cq.Workplane:
    """45° diamond bracing in the face plane between neighbouring fins, plus a top rail."""
    bars = []
    for left, right in zip(COLUMNS, COLUMNS[1:]):
        bay = cq.Solid.makeBox(right - left, FACE_T, STACK_TOP - BASE, cq.Vector(left, FACE_Y, BASE))
        diag = math.hypot(right - left, right - left)
        for k in range(int((STACK_TOP - BASE) // (right - left)) + 2):
            z = BASE + k * (right - left)
            for angle, x in ((45.0, left), (135.0, right)):
                bar = cq.Solid.makeBox(diag + 2 * LATTICE, FACE_T, LATTICE, cq.Vector(-LATTICE, 0, -LATTICE / 2.0))
                bar = bar.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), -angle).translate(cq.Vector(x, FACE_Y, z))
                bars.append(bar.intersect(bay))
    span = COLUMNS[-1] - COLUMNS[0]
    top = cq.Solid.makeBox(span, FACE_T, LATTICE, cq.Vector(COLUMNS[0], FACE_Y, STACK_TOP - LATTICE))
    return _compound(bars + [top])


def build_cradle() -> cq.Workplane:
    base = cq.Workplane("XY").box(WIDTH, FACE_Y + FACE_T - (BRICK_FRONT - 2.0), BASE, centered=False).translate(
        (-WIDTH / 2.0, BRICK_FRONT - 2.0, 0)).edges("|Z").fillet(2.0)
    rail = cq.Workplane("XY").box(COLUMNS[-1] - COLUMNS[0] + FIN_T, BACK_RAIL, BASE, centered=False).translate(
        (COLUMNS[0] - FIN_T / 2.0, SHELF_DEPTH - CORNER_CHAMFER - BACK_RAIL, 0))
    body = base.union(rail)
    for x in COLUMNS:
        body = body.union(_fin(x))
    body = body.union(_lattice())

    pocket = gf.stacking_pocket(POCKET_WALL, THICK)
    centre_y = BRICK_FRONT + THICK / 2.0
    return body.cut(_compound([pocket.translate((x, centre_y, BASE)).val() for x in COLUMNS]))


def split_cradle() -> tuple[cq.Workplane, cq.Workplane]:
    """The base piece in print pose, and the topper flipped onto its top face with pegs up."""
    full = build_cradle()
    big = 1000.0
    below = cq.Workplane("XY").box(big, big, SPLIT, centered=(True, True, False))
    above = cq.Workplane("XY").box(big, big, big, centered=(True, True, False)).translate((0, 0, SPLIT))
    peg_y = FACE_Y + FIN_FRAME / 2.0
    holes = [
        cq.Solid.makeBox(PEG + 2 * PEG_CLEAR, PEG + 2 * PEG_CLEAR, PEG_LEN + 0.5 + 1.0,
                         cq.Vector(x - PEG / 2.0 - PEG_CLEAR, peg_y - PEG / 2.0 - PEG_CLEAR, SPLIT - PEG_LEN - 0.5))
        for x in COLUMNS
    ]
    pegs = [
        cq.Solid.makeBox(PEG, PEG, PEG_LEN + 0.5, cq.Vector(x - PEG / 2.0, peg_y - PEG / 2.0, SPLIT - PEG_LEN))
        for x in COLUMNS
    ]
    base = full.intersect(below).cut(_compound(holes))
    top = full.intersect(above).union(_compound(pegs))
    top = top.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, STACK_TOP))
    return base, top


def _report(name: str, shape: cq.Workplane) -> None:
    solids = len(shape.val().Solids())
    bb = shape.val().BoundingBox()
    print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, {shape.val().Volume() / 1000:.0f} cm³, {solids} solid(s)")
    if solids != 1:
        raise SystemExit(f"{name} fragmented into {solids} solids")
    print(f"  {export_stl(shape, name)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Shelf cradle for a stack of battery bricks, in two pieces")
    parser.parse_args()
    base, top = split_cradle()
    _report("cradle-base", base)
    _report("cradle-top", top)
    cos, sin = math.cos(math.radians(SHELF_ANGLE)), math.sin(math.radians(SHELF_ANGLE))
    top_front = STACK_TOP * cos - BRICK_FRONT * sin
    print(f"  split at {SPLIT:.1f} mm; brick fronts {BRICK_FRONT:.1f} mm back from the shelf edge, "
          f"stack top {STACK_TOP:.1f} mm off the board")
    print(f"  highest corner {top_front:.1f} mm above the board's front edge ({OPENING:.0f} mm clear)")


if __name__ == "__main__":
    main()
