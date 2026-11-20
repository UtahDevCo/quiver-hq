from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq

from . import gridfinity as gf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
BUILD_DIR = PROJECT_ROOT / "build"


def load(name: str) -> dict:
    return json.loads((CONFIG_DIR / name).read_text())


def open_bin(spec: dict, bin_cfg: dict) -> cq.Workplane:
    nx, ny, h = spec["nx"], spec["ny"], spec["height_mm"]
    wall, floor = bin_cfg["wall_mm"], bin_cfg["floor_mm"]
    w, d = gf.outer_dims(nx, ny)
    pocket = (
        cq.Workplane("XY")
        .placeSketch(gf.rrect(w - 2 * wall, d - 2 * wall, gf.R_TOP - wall))
        .extrude(h)
        .edges("<Z")
        .fillet(bin_cfg["inner_fillet_mm"])
        .translate((0, 0, floor))
    )
    return gf.bin_shell(nx, ny, h).cut(pocket)


def _rect_points(w: float, l: float) -> list[list[float]]:
    return [[-w / 2, -l / 2], [w / 2, -l / 2], [w / 2, l / 2], [-w / 2, l / 2]]


def pockets(item: dict) -> list[tuple[list[tuple[float, float]], float]]:
    """Each pocket of an item as (box-frame outline points, depth)."""
    parts = item.get("parts") or [item]
    a = math.radians(item.get("rotate", 0))
    cx, cy = item["center"]
    out = []
    for part in parts:
        pts = part.get("points") or _rect_points(*part["size"])
        placed = [
            (x * math.cos(a) - y * math.sin(a) + cx, x * math.sin(a) + y * math.cos(a) + cy)
            for x, y in pts
        ]
        out.append((placed, part["depth_mm"]))
    return out


def fingers(item: dict) -> list[tuple[float, float]]:
    cx, cy = item["center"]
    return [(cx + dx, cy + dy) for dx, dy in item.get("finger", [])]


def _extent(item: dict) -> tuple[float, float]:
    xs, ys = zip(*(p for pts, _ in pockets({**item, "center": [0, 0]}) for p in pts))
    return max(xs) - min(xs), max(ys) - min(ys)


def placed_items(spec: dict, shadow: dict) -> list[dict]:
    """Items with centers. A box with lanes gets equal walls across and fills each lane from the back."""
    box = shadow["boxes"][spec["shadow"]]
    if "lanes" not in box:
        return box["items"]
    c2 = 2 * shadow["clearance_mm"]
    w, d = gf.outer_dims(spec["nx"], spec["ny"])
    widths = [max(_extent(it)[0] for it in lane) + c2 for lane in box["lanes"]]
    wall = (w - sum(widths)) / (len(widths) + 1)
    out, x = [], -w / 2 + wall
    for lane, lw in zip(box["lanes"], widths):
        y = d / 2 - wall
        for it in lane:
            length = _extent(it)[1] + c2
            out.append({**it, "center": [x + lw / 2, y - length / 2]})
            y -= length + wall
        if y < -d / 2:
            raise ValueError(f"lane starting with {lane[0]['name']} overruns the box by {-d / 2 - y:.1f} mm")
        x += lw + wall
    return out


def shadow_box(spec: dict, shadow: dict) -> cq.Workplane:
    top = spec["height_mm"] - gf.FOOT_H
    body = gf.bin_shell(spec["nx"], spec["ny"], spec["height_mm"])
    clearance = shadow["clearance_mm"]
    items = placed_items(spec, shadow)
    # One cut per pocket: overlapping cutters in one compound fragment the solid.
    for item in items:
        for pts, depth in pockets(item):
            pocket = (
                cq.Workplane("XY")
                .polyline(pts)
                .close()
                .offset2D(clearance, "arc")
                .extrude(depth + 1.0)
                .translate((0, 0, top - depth))
            )
            body = body.cut(pocket)
    r = shadow["finger_dia_mm"] / 2.0
    for item in items:
        depth = min(d for _, d in pockets(item))
        for fx, fy in fingers(item):
            notch = (
                cq.Workplane("XY")
                .center(fx, fy)
                .circle(r)
                .extrude(depth + 1.0)
                .translate((0, 0, top - depth))
            )
            body = body.cut(notch)
    return body


def export_stl(shape: cq.Workplane, name: str) -> Path:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    path = BUILD_DIR / f"{name}.stl"
    cq.exporters.export(shape, str(path), exportType="STL", tolerance=0.05)
    solids = len(shape.val().Solids()) if hasattr(shape.val(), "Solids") else 1
    bb = shape.val().BoundingBox()
    print(f"{path.name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, solids={solids}")
    return path


def layout_svg(cfg: dict, shadow: dict) -> Path:
    """Top-down plan of the drawer: grid, bins, and shadow-box pockets. Front of drawer at the bottom."""
    s = 2.0  # px per mm
    dw, dd = cfg["drawer"]["width_mm"], cfg["drawer"]["depth_mm"]
    nx, ny = cfg["grid"]["nx"], cfg["grid"]["ny"]
    ox = (dw - nx * gf.GRID) / 2.0
    oy = (dd - ny * gf.GRID) / 2.0
    pad = 20
    W, H = dw * s + 2 * pad, dd * s + 2 * pad

    def X(x: float) -> float:
        return pad + x * s

    def Y(y: float) -> float:
        return pad + (dd - y) * s

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
        f'font-family="Helvetica, Arial, sans-serif">',
        f'<rect width="{W:.0f}" height="{H:.0f}" fill="#fff"/>',
        f'<rect x="{X(0)}" y="{Y(dd)}" width="{dw * s}" height="{dd * s}" fill="#f4f4f4" stroke="#333" stroke-width="2"/>',
    ]
    for i in range(nx + 1):
        x = X(ox + i * gf.GRID)
        out.append(f'<line x1="{x}" y1="{Y(oy)}" x2="{x}" y2="{Y(oy + ny * gf.GRID)}" stroke="#ccc"/>')
    for j in range(ny + 1):
        y = Y(oy + j * gf.GRID)
        out.append(f'<line x1="{X(ox)}" y1="{y}" x2="{X(ox + nx * gf.GRID)}" y2="{y}" stroke="#ccc"/>')
    for b in cfg["bins"]:
        x0 = ox + b["col"] * gf.GRID + 0.25
        y0 = oy + b["row"] * gf.GRID + 0.25
        w, d = gf.outer_dims(b["nx"], b["ny"])
        fill = "#dbe9f7" if b["kind"] == "shadow" else "#e6f2e1"
        out.append(
            f'<rect x="{X(x0)}" y="{Y(y0 + d)}" width="{w * s}" height="{d * s}" rx="{gf.R_TOP * s}" '
            f'fill="{fill}" stroke="#2b4a6b" stroke-width="1.5"/>'
        )
        cx, cy = X(x0 + w / 2), Y(y0 + d / 2)
        if b["kind"] == "shadow":
            for item in placed_items(b, shadow):
                bx, by = x0 + w / 2, y0 + d / 2
                for pts, _ in pockets(item):
                    poly = " ".join(f"{X(bx + px):.1f},{Y(by + py):.1f}" for px, py in pts)
                    out.append(f'<polygon points="{poly}" fill="#9db8d6" stroke="#2b4a6b"/>')
                for fx, fy in fingers(item):
                    out.append(
                        f'<circle cx="{X(bx + fx)}" cy="{Y(by + fy)}" r="{shadow["finger_dia_mm"] / 2 * s}" '
                        f'fill="none" stroke="#2b4a6b" stroke-dasharray="4 3"/>'
                    )
                xs = [p[0] for pts, _ in pockets(item) for p in pts]
                ys = [p[1] for pts, _ in pockets(item) for p in pts]
                ix, iy = bx + (min(xs) + max(xs)) / 2, by + (min(ys) + max(ys)) / 2
                rot = -90 if max(ys) - min(ys) > max(xs) - min(xs) else 0
                out.append(
                    f'<text x="{X(ix)}" y="{Y(iy)}" font-size="13" text-anchor="middle" dominant-baseline="middle" '
                    f'transform="rotate({rot} {X(ix)} {Y(iy)})">{item["name"]}</text>'
                )
            continue
        label = f'{b["name"]} ({b["nx"]}x{b["ny"]}, {b["height_mm"]} mm)'
        rot = -90 if b["nx"] == 1 else 0
        out.append(
            f'<text x="{cx}" y="{cy - 9}" font-size="15" font-weight="bold" text-anchor="middle" '
            f'transform="rotate({rot} {cx} {cy})">{label}</text>'
        )
        if b["nx"] > 1:
            for k, line in enumerate(b["holds"].split(", ")):
                out.append(f'<text x="{cx}" y="{cy + 13 + 15 * k}" font-size="12" text-anchor="middle">{line}</text>')
    out.append(f'<text x="{W / 2}" y="{H - 4}" font-size="13" text-anchor="middle">drawer front</text>')
    out.append("</svg>")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    path = BUILD_DIR / "layout.svg"
    path.write_text("\n".join(out))
    print(path.name)
    return path


def main() -> None:
    p = argparse.ArgumentParser(description="Build the vanity drawer Gridfinity set")
    p.add_argument("--only", help="build one part by name (a bin or baseplate)")
    p.add_argument("--layout-only", action="store_true", help="write build/layout.svg and stop")
    args = p.parse_args()

    cfg = load("drawer.json")
    shadow = load("shadow.json")
    layout_svg(cfg, shadow)
    if args.layout_only:
        return

    bp = cfg["baseplates"]
    for plate in bp["plates"]:
        if args.only in (None, plate["name"]):
            export_stl(gf.baseplate(cfg["grid"]["nx"], plate["ny"], pad_x=bp["side_pad_mm"]), plate["name"])
    for b in cfg["bins"]:
        if args.only not in (None, b["name"]):
            continue
        if b["kind"] == "shadow":
            export_stl(shadow_box(b, shadow), b["name"])
        else:
            export_stl(open_bin(b, cfg["bin"]), b["name"])


if __name__ == "__main__":
    main()
