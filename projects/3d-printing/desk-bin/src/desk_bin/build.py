from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

import cadquery as cq

from . import bin as desk_bin

BUILD_DIR = Path(__file__).resolve().parents[2] / "build"

PARTS: dict[str, Callable[[], cq.Workplane]] = {
    "body": desk_bin.body,
    "lid": desk_bin.lid_print,
    "flap": desk_bin.flap_print,
    "pin": desk_bin.pin_print,
    "assembly-preview": desk_bin.assembly,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the desk bin as STL.")
    parser.add_argument("--only", choices=sorted(PARTS), action="append")
    args = parser.parse_args()

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    for name in args.only or sorted(PARTS):
        path = BUILD_DIR / f"{name}.stl"
        cq.exporters.export(PARTS[name](), str(path), exportType="STL", tolerance=0.05)
        print(path)
