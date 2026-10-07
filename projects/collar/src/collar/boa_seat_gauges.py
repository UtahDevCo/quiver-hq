"""Small, numbered S2-S *seat* gauges for bench-only PLA fit testing.

The two measured underside diameters are useful, but the S2-S snap-window
undercuts have not been measured well enough to print a trustworthy latch.
These gauges intentionally have no retaining hooks.  Their job is to check
which (if any) stepped recess accepts the removable cartridge without force.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq

from .config import PROJECT_ROOT


OUTER_MEASURED_MM = 20.45
INNER_MEASURED_MM = 18.73
CLEARANCES_MM = (0.10, 0.30, 0.50, 0.70)  # diametric, not radial
BODY_THICKNESS_MM = 5.0
FIRST_STEP_DEPTH_MM = 1.15
SECOND_STEP_DEPTH_MM = 2.21


def make_gauge(number: int, diametric_clearance: float) -> cq.Shape:
    """Make one open, non-retaining stepped recess and an integral number tab."""
    if number not in (1, 2, 3, 4):
        raise ValueError("Gauge number must be 1 through 4")

    body = cq.Workplane("XY").circle(16.0).extrude(BODY_THICKNESS_MM)
    tab = (
        cq.Workplane("XY")
        .center(19.0, 0)
        .rect(18.0, 14.0)
        .extrude(BODY_THICKNESS_MM)
    )
    body = body.union(tab)

    # The upper pocket clears the larger measured step; the lower pocket
    # clears the smaller step. This order is an explicit, testable assumption.
    upper_diameter = OUTER_MEASURED_MM + diametric_clearance
    lower_diameter = INNER_MEASURED_MM + diametric_clearance
    upper = (
        cq.Workplane("XY")
        .workplane(offset=BODY_THICKNESS_MM - FIRST_STEP_DEPTH_MM)
        .circle(upper_diameter / 2)
        .extrude(FIRST_STEP_DEPTH_MM + 0.05)
    )
    lower = (
        cq.Workplane("XY")
        .workplane(offset=BODY_THICKNESS_MM - SECOND_STEP_DEPTH_MM)
        .circle(lower_diameter / 2)
        .extrude(SECOND_STEP_DEPTH_MM + 0.05)
    )
    body = body.cut(upper).cut(lower)

    # Give both captive laces an escape path; this is a geometry check, not a
    # tensile or retention test.  Channels are intentionally wider than lace.
    for side in (-1, 1):
        channel = (
            cq.Workplane("XY")
            .workplane(offset=BODY_THICKNESS_MM - 2.5)
            .center(side * 14.0, 0)
            .rect(12.0, 2.0)
            .extrude(2.55)
        )
        body = body.cut(channel)

    number_mark = (
        cq.Workplane("XY")
        .workplane(offset=BODY_THICKNESS_MM)
        .center(21.5, 0)
        .text(str(number), 8.0, 0.6, combine=True)
    )
    solid = body.union(number_mark).val()
    if not solid.isValid() or len(solid.Solids()) != 1:
        raise RuntimeError(f"Gauge {number} is not a single valid solid")
    return solid


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "build" / "boa-seat-gauges",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    parts: list[cq.Shape] = []
    manifest = []
    for number, clearance in enumerate(CLEARANCES_MM, start=1):
        gauge = make_gauge(number, clearance)
        name = f"boa-s2s-seat-{number}.stl"
        cq.exporters.export(gauge, str(args.output_dir / name))
        column, row = (number - 1) % 2, (number - 1) // 2
        parts.append(gauge.translate(cq.Vector(column * 48.0, row * 42.0, 0)))
        manifest.append(
            {
                "number": number,
                "file": name,
                "diametric_clearance_mm": clearance,
                "upper_recess_diameter_mm": round(OUTER_MEASURED_MM + clearance, 2),
                "lower_recess_diameter_mm": round(INNER_MEASURED_MM + clearance, 2),
            }
        )

    cq.exporters.export(
        cq.Compound.makeCompound(parts),
        str(args.output_dir / "boa-s2s-seat-gauges-1-to-4-plate.stl"),
    )
    (args.output_dir / "manifest.json").write_text(
        json.dumps({"gauges": manifest}, indent=2) + "\n"
    )
    print(f"Wrote four numbered gauges to {args.output_dir}")


if __name__ == "__main__":
    main()
