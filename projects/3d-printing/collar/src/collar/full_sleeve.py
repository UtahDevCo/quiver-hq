from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient

from .config import DEFAULT_CONFIG, PROJECT_ROOT, load_config, resolve_project_path
from .fit_gauges import (
    _largest_polygon,
    _neck_polygon,
    _section_segments,
    _symmetrize_polygon,
)
from .scan import inspect_binary_stl


def _canonical_points(
    polygon: Polygon,
    center_x: float,
    point_count: int,
) -> list[tuple[float, float]]:
    """Sample a contour from its posterior center with consistent winding."""
    polygon = orient(polygon, sign=1.0)
    ring = LineString(polygon.exterior.coords)
    posterior_center = Point(center_x, polygon.bounds[1])
    start_distance = ring.project(posterior_center)
    return [
        tuple(
            ring.interpolate(
                (start_distance + index * ring.length / point_count) % ring.length
            ).coords[0]
        )
        for index in range(point_count)
    ]


def _loft_wire(
    polygon: Polygon,
    level_y: float,
    center_x: float,
    point_count: int,
) -> cq.Wire:
    points = _canonical_points(polygon, center_x, point_count)
    return cq.Wire.makePolygon(
        [cq.Vector(float(x), level_y, float(z)) for x, z in points],
        close=True,
    )


def _fit_neck_axis(
    centers: list[tuple[float, float, float]],
) -> np.ndarray:
    """Fit a Y-forward centerline and return its unit direction vector."""
    if len(centers) < 2:
        raise ValueError("Neck-axis alignment requires at least two sections")
    samples = np.asarray(centers, dtype=float)
    slope_x, _ = np.polyfit(samples[:, 1], samples[:, 0], 1)
    slope_z, _ = np.polyfit(samples[:, 1], samples[:, 2], 1)
    axis = np.asarray((slope_x, 1.0, slope_z), dtype=float)
    return axis / np.linalg.norm(axis)


def _plane_basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return local left/right and posterior/anterior axes normal to axis."""
    global_x = np.asarray((1.0, 0.0, 0.0))
    local_x = global_x - axis * np.dot(global_x, axis)
    local_x /= np.linalg.norm(local_x)
    local_z = np.cross(local_x, axis)
    local_z /= np.linalg.norm(local_z)
    return local_x, local_z


def _project_polygon_to_plane(
    polygon: Polygon,
    level_y: float,
    center: np.ndarray,
    local_x: np.ndarray,
    local_z: np.ndarray,
) -> Polygon:
    points = np.asarray(
        [(x, level_y, z) for x, z in polygon.exterior.coords[:-1]],
        dtype=float,
    )
    relative = points - center
    projected = Polygon(
        np.column_stack((relative @ local_x, relative @ local_z))
    ).buffer(0)
    if projected.is_empty:
        raise ValueError("Neck contour projection produced an empty polygon")
    return _largest_polygon(projected)


def _local_to_scan_matrix(
    center: np.ndarray,
    local_x: np.ndarray,
    axis: np.ndarray,
    local_z: np.ndarray,
) -> cq.Matrix:
    return cq.Matrix(
        [
            [local_x[0], axis[0], local_z[0], center[0]],
            [local_x[1], axis[1], local_z[1], center[1]],
            [local_x[2], axis[2], local_z[2], center[2]],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


def _fourier_smooth_polygon(
    polygon: Polygon,
    point_count: int,
    harmonics: int,
) -> Polygon:
    """Low-pass a closed contour while retaining its overall neck shape."""
    if point_count < 16:
        raise ValueError("Outer-interface smoothing requires at least 16 points")
    if harmonics < 2 or harmonics >= point_count // 2:
        raise ValueError("Outer-interface harmonics are out of range")
    points = np.asarray(
        _canonical_points(polygon, polygon.centroid.x, point_count),
        dtype=float,
    )
    spectrum = np.fft.fft(points, axis=0)
    spectrum[harmonics + 1 : -harmonics] = 0.0
    smoothed = Polygon(np.fft.ifft(spectrum, axis=0).real).buffer(0)
    if smoothed.is_empty:
        raise ValueError("Outer-interface smoothing produced an empty polygon")
    return _largest_polygon(smoothed)


def _smooth_containing_envelope(
    required: Polygon,
    point_count: int,
    harmonics: int,
) -> tuple[Polygon, float]:
    """Smooth a profile and expand it just enough to preserve minimum wall."""
    smoothed = _fourier_smooth_polygon(required, point_count, harmonics)
    if smoothed.covers(required):
        return smoothed, 0.0

    lower = 0.0
    upper = 0.25
    while not smoothed.buffer(upper).covers(required):
        upper *= 2.0
        if upper > 32.0:
            raise ValueError("Could not form a containing outer-interface envelope")
    for _ in range(18):
        middle = (lower + upper) / 2.0
        if smoothed.buffer(middle).covers(required):
            upper = middle
        else:
            lower = middle
    return _largest_polygon(smoothed.buffer(upper)), upper


def _hourglass_sections(
    reference_level: float,
    core_height: float,
    flare_height: float,
    flare_outset: float,
    flare_steps: int,
) -> list[tuple[float, float]]:
    """Return stations around a fitted core centered on reference_level."""
    if core_height <= 0.0 or flare_height <= 0.0 or flare_outset <= 0.0:
        raise ValueError("Full-sleeve hourglass dimensions must be positive")
    if flare_steps < 2:
        raise ValueError("Full-sleeve flares require at least two steps")

    core_bottom = reference_level - core_height / 2.0
    core_top = reference_level + core_height / 2.0

    def smooth_outset(step: int) -> float:
        fraction = step / flare_steps
        return flare_outset * (1.0 - math.cos(math.pi * fraction)) / 2.0

    bottom = [
        (
            core_bottom - flare_height * step / flare_steps,
            smooth_outset(step),
        )
        for step in range(flare_steps, 0, -1)
    ]
    core = [(core_bottom, 0.0), (core_top, 0.0)]
    top = [
        (
            core_top + flare_height * step / flare_steps,
            smooth_outset(step),
        )
        for step in range(1, flare_steps + 1)
    ]
    return bottom + core + top


def _build_full_sleeve_shapes(
    config: dict,
) -> tuple[cq.Shape, cq.Shape, dict]:
    scan_path = resolve_project_path(config, config["scan"])
    report = inspect_binary_stl(scan_path, float(config["scale_to_mm"]))
    neck_config = config["neck"]
    sleeve_config = config["full_sleeve"]
    alignment_config = sleeve_config["alignment"]
    symmetry = neck_config["symmetry"]
    reference_level = float(sleeve_config["reference_level_y_mm"])
    point_count = int(sleeve_config["contour_points"])
    core_height = float(sleeve_config["core_height_mm"])
    flare_height = float(sleeve_config["flare_height_mm"])
    flare_outset = float(sleeve_config["flare_outset_mm"])
    stations = _hourglass_sections(
        0.0,
        core_height,
        flare_height,
        flare_outset,
        int(sleeve_config["flare_steps"]),
    )

    segments = _section_segments(
        scan_path,
        report["triangle_count"],
        reference_level,
        float(config["scale_to_mm"]),
    )
    raw_neck = _neck_polygon(
        segments,
        (
            float(neck_config["expected_center_x_mm"]),
            float(neck_config["expected_center_z_mm"]),
        ),
        float(neck_config["section_search_radius_mm"]),
    )
    if symmetry["enabled"]:
        reference_neck, common_center_x = _symmetrize_polygon(
            raw_neck,
            int(symmetry["samples"]),
            int(symmetry["smoothing_window"]),
        )
    else:
        reference_neck = raw_neck
        common_center_x = (raw_neck.bounds[0] + raw_neck.bounds[2]) / 2.0

    alignment_samples: list[tuple[float, float, float]] = []
    if alignment_config["enabled"]:
        for level in alignment_config["section_levels_y_mm"]:
            level = float(level)
            section = _neck_polygon(
                _section_segments(
                    scan_path,
                    report["triangle_count"],
                    level,
                    float(config["scale_to_mm"]),
                ),
                (
                    float(neck_config["expected_center_x_mm"]),
                    float(neck_config["expected_center_z_mm"]),
                ),
                float(neck_config["section_search_radius_mm"]),
            )
            alignment_samples.append(
                (float(section.centroid.x), level, float(section.centroid.y))
            )
        neck_axis = _fit_neck_axis(alignment_samples)
    else:
        neck_axis = np.asarray((0.0, 1.0, 0.0))

    reference_center = np.asarray(
        (common_center_x, reference_level, reference_neck.centroid.y),
        dtype=float,
    )
    local_x, local_z = _plane_basis(neck_axis)
    local_reference = _project_polygon_to_plane(
        reference_neck,
        reference_level,
        reference_center,
        local_x,
        local_z,
    )

    clearance = float(sleeve_config["clearance_mm"])
    wall = float(sleeve_config["wall_thickness_mm"])
    outer_interface = sleeve_config["outer_interface"]
    inner_sections: list[tuple[float, Polygon]] = []
    outer_sections: list[tuple[float, Polygon]] = []
    smoothing_expansion: list[float] = []

    for level, outset in stations:
        inner = _largest_polygon(local_reference.buffer(clearance + outset))
        required_outer = _largest_polygon(inner.buffer(wall))
        outer, expansion = _smooth_containing_envelope(
            required_outer,
            int(outer_interface["samples"]),
            int(outer_interface["harmonics"]),
        )
        inner_sections.append((level, inner))
        outer_sections.append((level, outer))
        smoothing_expansion.append(expansion)

    outer_wires = [
        _loft_wire(section, level, local_reference.centroid.x, point_count)
        for level, section in outer_sections
    ]
    inner_wires = [
        _loft_wire(section, level, local_reference.centroid.x, point_count)
        for level, section in inner_sections
    ]

    ruled_loft = bool(sleeve_config["ruled_loft"])
    outer_solid = cq.Solid.makeLoft(outer_wires, ruled=ruled_loft)
    inner_solid = cq.Solid.makeLoft(inner_wires, ruled=ruled_loft)
    local_sleeve = outer_solid.cut(inner_solid)

    reference_inner = _largest_polygon(local_reference.buffer(clearance))
    levels = [level for level, _ in stations]
    min_y, max_y = min(levels), max(levels)
    min_posterior_z = min(section.bounds[1] for _, section in outer_sections)
    rear_cut_end_z = reference_inner.centroid.y
    rear_gap = float(sleeve_config["rear_gap_mm"])
    gap_cut = cq.Solid.makeBox(
        rear_gap,
        max_y - min_y + 20.0,
        rear_cut_end_z - min_posterior_z + 30.0,
        cq.Vector(
            reference_inner.centroid.x - rear_gap / 2.0,
            min_y - 10.0,
            min_posterior_z - 20.0,
        ),
    )
    local_sleeve = local_sleeve.cut(gap_cut)
    sleeve = local_sleeve.transformGeometry(
        _local_to_scan_matrix(reference_center, local_x, neck_axis, local_z)
    )

    if not sleeve.isValid() or len(sleeve.Solids()) != 1:
        raise ValueError("Full-sleeve loft did not produce one valid solid")

    bbox = sleeve.BoundingBox()
    metadata = {
        "scan": report,
        "profile_mode": sleeve_config["profile_mode"],
        "loft_stations": [
            {
                "axis_offset_mm": offset,
                "center_scan_mm": (
                    reference_center + neck_axis * offset
                ).tolist(),
                "outset_mm": outset,
            }
            for offset, outset in stations
        ],
        "reference_level_y_mm": reference_level,
        "reference_center_scan_mm": reference_center.tolist(),
        "alignment_enabled": bool(alignment_config["enabled"]),
        "alignment_section_centers_mm": [list(item) for item in alignment_samples],
        "neck_axis_scan": neck_axis.tolist(),
        "neck_axis_forward_tilt_degrees": math.degrees(
            math.atan2(neck_axis[2], neck_axis[1])
        ),
        "neck_axis_lateral_tilt_degrees": math.degrees(
            math.atan2(neck_axis[0], neck_axis[1])
        ),
        "symmetry_center_x_mm": common_center_x,
        "core_height_mm": core_height,
        "flare_height_mm": flare_height,
        "flare_outset_mm": flare_outset,
        "ruled_loft": ruled_loft,
        "clearance_mm": clearance,
        "wall_thickness_mm": wall,
        "outer_interface": {
            "mode": outer_interface["mode"],
            "samples": int(outer_interface["samples"]),
            "harmonics": int(outer_interface["harmonics"]),
            "maximum_envelope_expansion_mm": max(smoothing_expansion),
        },
        "rear_gap_mm": rear_gap,
        "observed_rear_overlap_mm": float(
            sleeve_config["observed_rear_overlap_mm"]
        ),
        "overlap_correction_applied": bool(
            sleeve_config["apply_overlap_correction"]
        ),
        "scan_coordinate_dimensions_mm": [bbox.xlen, bbox.ylen, bbox.zlen],
        "volume_mm3": sleeve.Volume(),
    }
    return sleeve, local_sleeve, metadata


def build_full_sleeve(config: dict) -> tuple[cq.Shape, dict]:
    sleeve, _, metadata = _build_full_sleeve_shapes(config)
    return sleeve, metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Melissa's scan-derived full inner collar sleeve."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "build" / "full-sleeve",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    sleeve, local_sleeve, metadata = _build_full_sleeve_shapes(config)
    args.output.mkdir(parents=True, exist_ok=True)

    step_path = args.output / "melissa-inner-sleeve-prototype.step"
    stl_path = args.output / "melissa-inner-sleeve-prototype.stl"
    manifest_path = args.output / "manifest.json"

    cq.exporters.export(sleeve, str(step_path))
    # Print from the sleeve's local frame rather than scan space. The fitted
    # neck axis becomes print Z and the complete lower C-shaped rim is planar.
    print_sleeve = local_sleeve.rotate((0, 0, 0), (1, 0, 0), 90.0)
    print_sleeve = print_sleeve.translate(
        (0.0, 0.0, -print_sleeve.BoundingBox().zmin)
    )
    cq.exporters.export(
        print_sleeve,
        str(stl_path),
        tolerance=0.08,
        angularTolerance=0.15,
    )

    print_bbox = print_sleeve.BoundingBox()
    metadata.update(
        {
            "stl": str(stl_path),
            "stl_coordinate_system": "local-neck-axis-z-up",
            "stl_orientation": "lower-flare-rim-flat-on-bed",
            "stl_dimensions_mm": [
                print_bbox.xlen,
                print_bbox.ylen,
                print_bbox.zlen,
            ],
            "step": str(step_path),
            "step_coordinate_system": "scan-y-up",
        }
    )
    manifest_path.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"wrote {stl_path}")
    print(f"wrote {step_path}")


if __name__ == "__main__":
    main()
