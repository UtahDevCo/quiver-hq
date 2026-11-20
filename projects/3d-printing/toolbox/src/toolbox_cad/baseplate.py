"""Open-frame Gridfinity baseplate sized to a drawer, split into bed-sized pieces.

The frame has no floor: a bin's 4.75 mm foot drops through the 4.65 mm socket and
stands on the drawer floor, so the plate adds no height under the bins. The
socket profile is the gridfinity-rebuilt baseplate profile: from the top, a
2.15 mm 45-degree taper, 1.8 mm straight, 0.7 mm 45-degree chamfer, with a 4.0 mm
top corner radius (the bin foot's 3.75 plus its 0.25 clearance).

Spare drawer width becomes a solid margin on both long sides so the plate cannot
shift. Along the drawer's depth the cells fill the length, and only the outermost
edge is trimmed (`end_trim`) to leave fitting clearance at the front and back.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq

GRID = 42.0
H = 4.65                       # 2.15 taper + 1.8 straight + 0.7 chamfer
TAPER, STRAIGHT, CHAMFER = 2.15, 1.8, 0.7
R_TOP = 4.0

# Drawer inside, from the caliper sheet (2026-11-05).
DRAWER_W = 258.8
DRAWER_D = 504.8
FIT = 0.25                     # clearance per side between plate and drawer wall


def _rrect(size: float, r: float, z: float) -> cq.Sketch:
    return cq.Sketch().rect(size, size).reset().vertices().fillet(r).moved(cq.Location(cq.Vector(0, 0, z)))


def socket_cutter() -> cq.Workplane:
    """The void of one cell, top at z=H, cut through the bottom."""
    s_top, s_mid, s_bot = GRID, GRID - 2 * TAPER, GRID - 2 * (TAPER + CHAMFER)
    r_mid, r_bot = R_TOP - TAPER, R_TOP - TAPER - CHAMFER
    taper = cq.Workplane("XY").placeSketch(_rrect(s_mid, r_mid, H - TAPER), _rrect(s_top, R_TOP, H + 0.01)).loft()
    straight = cq.Workplane("XY").placeSketch(_rrect(s_mid, r_mid, CHAMFER), _rrect(s_mid, r_mid, H - TAPER)).loft()
    chamfer = cq.Workplane("XY").placeSketch(_rrect(s_bot, r_bot, 0.0), _rrect(s_mid, r_mid, CHAMFER)).loft()
    through = cq.Workplane("XY").placeSketch(_rrect(s_bot, r_bot, -1.0), _rrect(s_bot, r_bot, 0.0)).loft()
    return taper.union(straight).union(chamfer).union(through)


def piece(nx: int, ny: int, side_margin: float, trim_front: float, trim_back: float,
          corner_r: float) -> cq.Workplane:
    """nx by ny cells (x across the drawer, y along it). Cells sit at x in
    [side_margin, side_margin + 42 nx] and y in [0, 42 ny] before trimming; the
    front (y=0) and back (y=42 ny) faces are then cut back by the trims.
    Corners on a trimmed (drawer end) face get `corner_r`; joint faces stay square."""
    w = nx * GRID + 2 * side_margin
    y0, y1 = trim_front, ny * GRID - trim_back
    plate = cq.Workplane("XY").box(w, y1 - y0, H, centered=False).translate((0, y0, 0))
    edges = []
    if trim_front > 0:
        edges += [(0, y0), (w, y0)]
    if trim_back > 0:
        edges += [(0, y1), (w, y1)]
    for ex, ey in edges:
        plate = plate.edges(cq.selectors.NearestToPointSelector((ex, ey, H / 2))).fillet(corner_r)
    cutter = socket_cutter()
    cells = None
    for i in range(nx):
        for j in range(ny):
            c = cutter.translate((side_margin + (i + 0.5) * GRID, (j + 0.5) * GRID, 0))
            cells = c if cells is None else cells.union(c)
    return plate.cut(cells)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="build/baseplate")
    ap.add_argument("--end-trim", type=float, default=0.5, help="mm cut off the outer edge at the drawer front and back")
    ap.add_argument("--pieces", type=int, default=2, help="split along the drawer depth into this many pieces")
    args = ap.parse_args()

    nx = int((DRAWER_W - 2 * FIT) // GRID)
    ny = int((DRAWER_D - 2 * FIT + 2 * args.end_trim) // GRID)
    side = (DRAWER_W - 2 * FIT - nx * GRID) / 2
    plate_d = ny * GRID - 2 * args.end_trim
    end_gap = (DRAWER_D - plate_d) / 2
    print(f"drawer {DRAWER_W} x {DRAWER_D}: {nx} x {ny} cells, side margin {side:.2f} mm, "
          f"plate {nx * GRID + 2 * side:.1f} x {plate_d:.1f} mm, end gap {end_gap:.2f} mm per end")

    rows = [ny // args.pieces + (1 if k < ny % args.pieces else 0) for k in range(args.pieces)]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for k, n in enumerate(rows):
        front = args.end_trim if k == 0 else 0.0
        back = args.end_trim if k == len(rows) - 1 else 0.0
        part = piece(nx, n, side, front, back, corner_r=3.0)
        bb = part.val().BoundingBox()
        path = out / f"baseplate-{k + 1}of{len(rows)}-{nx}x{n}.stl"
        cq.exporters.export(part, str(path), tolerance=0.02, angularTolerance=0.1)
        print(f"{path}: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm, volume {part.val().Volume() / 1000:.1f} cm3")


if __name__ == "__main__":
    main()
