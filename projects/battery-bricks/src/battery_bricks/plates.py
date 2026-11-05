from __future__ import annotations

import argparse

import cadquery as cq

from .brick import BRICKS, build_brick
from .cells import BUILD_DIR
from .cradle import split_cradle
from .export import export_stl

# Qidi Plus 4: 305 x 305 x 280 mm. Parts go in a column down Y, centred in X, in
# print pose, with GAP between them so the slicer's own arrange can stay off.
BED = 305.0
MAX_Z = 280.0
GAP = 6.0


def _parts() -> dict[str, cq.Workplane]:
    base, top = split_cradle()
    parts = {"cradle-base": base, "cradle-top": top}
    parts.update({b.name: build_brick(b) for b in BRICKS})
    return parts


PLATES = {
    "plate-1": ("brick-21700", "brick-odds"),
    "plate-2": ("cradle-base", "cradle-top"),
}


def lay_out(shapes: list[tuple[str, cq.Workplane]]) -> list[tuple[str, cq.Workplane]]:
    boxes = [s.val().BoundingBox() for _, s in shapes]
    depth = sum(b.ylen for b in boxes) + GAP * (len(boxes) - 1)
    if depth > BED or any(b.xlen > BED or b.zlen > MAX_Z for b in boxes):
        raise SystemExit(f"plate does not fit: {depth:.1f} mm of {BED:.0f} along Y")
    y = (BED - depth) / 2.0
    out = []
    for (name, s), b in zip(shapes, boxes):
        moved = s.translate((BED / 2.0 - (b.xmin + b.xmax) / 2.0, y - b.ymin, -b.zmin))
        out.append((name, moved))
        y += b.ylen + GAP
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Export each print plate's parts already placed on the bed")
    parser.add_argument("plates", nargs="*", help="plates to export (default: all)")
    args = parser.parse_args()
    parts = _parts()
    for plate, names in PLATES.items():
        if args.plates and plate not in args.plates:
            continue
        print(plate)
        for name, shape in lay_out([(n, parts[n]) for n in names]):
            bb = shape.val().BoundingBox()
            path = export_stl(shape, name, BUILD_DIR / plate)
            print(f"  {name}: x {bb.xmin:.1f}..{bb.xmax:.1f}, y {bb.ymin:.1f}..{bb.ymax:.1f}, z to {bb.zmax:.1f}  {path}")


if __name__ == "__main__":
    main()
