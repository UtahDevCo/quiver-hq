from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

import cadquery as cq

from . import gridfinity as gf
from . import roof

BUILD_DIR = Path(__file__).resolve().parents[2] / "build"

PARTS: dict[str, Callable[[], cq.Workplane]] = {
    "drawer-tray-3x5-2u": lambda: gf.open_tray(3, 5, 2),
    "roof-slot-block-2x5-6u": roof.slot_block,
    "roof-tray-3x3-2u": lambda: gf.open_tray(3, 3, 2),
    "roof-tray-2x3-2u": lambda: gf.open_tray(2, 3, 2),
    "roof-tall-3x2-6u": lambda: gf.open_tray(3, 2, 6),
    "roof-watch-dish-2x2-3u": roof.watch_dish,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the nightstand bins as STL.")
    parser.add_argument("--only", choices=sorted(PARTS), action="append")
    args = parser.parse_args()

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    for name in args.only or sorted(PARTS):
        path = BUILD_DIR / f"{name}.stl"
        cq.exporters.export(PARTS[name](), str(path), exportType="STL", tolerance=0.05)
        print(path)
