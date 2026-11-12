from __future__ import annotations

from pathlib import Path

import cadquery as cq

from .config import BUILD_DIR


def export_stl(shape: cq.Workplane, name: str, out_dir: Path | None = None) -> Path:
    out = (out_dir or BUILD_DIR)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name}.stl"
    cq.exporters.export(shape, str(path), exportType="STL", tolerance=0.05)
    return path


def export_svg(
    shape: cq.Workplane,
    name: str,
    out_dir: Path | None = None,
    direction: tuple[float, float, float] = (-1.0, -1.0, 0.7),
) -> Path:
    out = (out_dir or BUILD_DIR)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name}.svg"
    opts = {
        "projectionDir": direction,
        "showAxes": False,
        "strokeWidth": 0.3,
    }
    cq.exporters.export(shape, str(path), exportType="SVG", opt=opts)
    return path
