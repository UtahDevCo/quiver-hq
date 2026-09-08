from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

import numpy as np

from .config import DEFAULT_CONFIG, load_config, resolve_project_path


STL_RECORD = np.dtype(
    [
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ]
)


def inspect_binary_stl(path: Path, scale: float) -> dict[str, Any]:
    size = path.stat().st_size
    with path.open("rb") as stream:
        header = stream.read(84)
    if len(header) != 84:
        raise ValueError(f"STL is too small to be binary: {path}")

    triangle_count = struct.unpack_from("<I", header, 80)[0]
    expected_size = 84 + triangle_count * STL_RECORD.itemsize
    if size != expected_size:
        raise ValueError(
            f"Expected a binary STL of {expected_size} bytes, found {size}: {path}"
        )

    triangles = np.memmap(
        path,
        dtype=STL_RECORD,
        mode="r",
        offset=84,
        shape=(triangle_count,),
    )
    vertices = triangles["vertices"]
    minimum = vertices.min(axis=(0, 1)).astype(np.float64) * scale
    maximum = vertices.max(axis=(0, 1)).astype(np.float64) * scale

    return {
        "path": str(path),
        "format": "binary-stl",
        "triangle_count": int(triangle_count),
        "scale_to_mm": scale,
        "bbox_min_mm": minimum.tolist(),
        "bbox_max_mm": maximum.tolist(),
        "dimensions_mm": (maximum - minimum).tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect the source neck scan.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    path = resolve_project_path(config, config["scan"])
    report = inspect_binary_stl(path, float(config["scale_to_mm"]))
    report["axes"] = config["axes"]

    if args.json:
        print(json.dumps(report, indent=2))
        return

    dims = report["dimensions_mm"]
    print(f"scan: {report['path']}")
    print(f"triangles: {report['triangle_count']:,}")
    print(f"scale: {report['scale_to_mm']:g} -> mm")
    print(f"dimensions: {dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} mm")
    print(f"axes: {report['axes']}")


if __name__ == "__main__":
    main()
