from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import cadquery as cq
import numpy as np
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.ops import linemerge, polygonize, unary_union

from .config import DEFAULT_CONFIG, PROJECT_ROOT, load_config, resolve_project_path
from .scan import STL_RECORD, inspect_binary_stl


def _section_segments(
    path: Path, triangle_count: int, level_y: float, scale: float
) -> np.ndarray:
    records = np.memmap(
        path,
        dtype=STL_RECORD,
        mode="r",
        offset=84,
        shape=(triangle_count,),
    )
    vertices = records["vertices"].astype(np.float64) * scale
    relative_y = vertices[:, :, 1] - level_y
    crossing = (relative_y.min(axis=1) <= 0.0) & (relative_y.max(axis=1) >= 0.0)
    triangles = vertices[crossing]

    segments: list[np.ndarray] = []
    for triangle in triangles:
        hits: list[np.ndarray] = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            va, vb = triangle[a], triangle[b]
            da, db = va[1] - level_y, vb[1] - level_y
            if da == 0.0 and db == 0.0:
                continue
            if da == 0.0:
                hits.append(va[[0, 2]])
            elif db == 0.0:
                hits.append(vb[[0, 2]])
            elif (da < 0.0) != (db < 0.0):
                t = -da / (db - da)
                point = va + t * (vb - va)
                hits.append(point[[0, 2]])
        if len(hits) >= 2 and not np.allclose(hits[0], hits[1]):
            segments.append(np.stack((hits[0], hits[1])))
    if not segments:
        raise ValueError(f"No mesh intersection found at Y={level_y:.2f} mm")
    return np.stack(segments)


def _neck_polygon(
    segments: np.ndarray,
    expected_center: tuple[float, float],
    search_radius: float,
) -> Polygon:
    # The source scan contains nearly coincident triangle vertices rather than a
    # perfectly welded manifold. A 0.1 mm quantization is far below the scan and
    # printer resolution, but reconnects the section into usable contour chains.
    quantized = np.round(segments, decimals=1)
    lines = [LineString(segment) for segment in quantized]
    united = unary_union(lines)
    polygons = list(polygonize(united))

    merged = linemerge(united)
    chains = list(merged.geoms) if hasattr(merged, "geoms") else [merged]
    for chain in chains:
        if chain.length < 10.0:
            continue
        endpoints = np.asarray((chain.coords[0], chain.coords[-1]))
        if np.linalg.norm(endpoints[0] - endpoints[1]) > 1.0:
            continue
        repaired = Polygon(chain.coords).buffer(0)
        if isinstance(repaired, Polygon) and repaired.area > 1.0:
            polygons.append(repaired)
        elif isinstance(repaired, MultiPolygon):
            polygons.extend(part for part in repaired.geoms if part.area > 1.0)

    if not polygons:
        raise ValueError("Section segments did not form any closed contours")

    center = np.asarray(expected_center, dtype=float)
    candidates = []
    for polygon in polygons:
        distance = np.linalg.norm(np.asarray(polygon.centroid.coords[0]) - center)
        if distance <= search_radius:
            candidates.append((distance, -polygon.area, polygon))
    if not candidates:
        raise ValueError(
            f"No closed contour lies within {search_radius:g} mm of {expected_center}"
        )
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][2]


def _resample_ring(polygon: Polygon, point_count: int) -> Polygon:
    ring = LineString(polygon.exterior.coords)
    samples = [
        ring.interpolate(index / point_count, normalized=True).coords[0]
        for index in range(point_count)
    ]
    return Polygon(samples).buffer(0)


def _symmetrize_polygon(
    polygon: Polygon,
    samples: int,
    smoothing_window: int,
) -> tuple[Polygon, float]:
    """Average left/right section widths around a stable lateral centerline.

    X is left/right and the Shapely Y coordinate represents scan Z
    (posterior/anterior). Keeping the original width at each Z preserves the
    fitted circumference while moving both sides equally onto a mirror pair.
    """
    min_x, min_z, max_x, max_z = polygon.bounds
    center_x = (min_x + max_x) / 2.0
    z_values = np.linspace(min_z, max_z, max(5, samples))
    span = max_x - min_x
    half_widths: list[float] = []

    for z in z_values:
        section = polygon.intersection(
            LineString(((min_x - span, z), (max_x + span, z)))
        )
        coordinates: list[tuple[float, float]] = []
        if section.is_empty:
            half_widths.append(0.0)
            continue
        geometries = list(section.geoms) if hasattr(section, "geoms") else [section]
        for geometry in geometries:
            if hasattr(geometry, "coords"):
                coordinates.extend(geometry.coords)
        if not coordinates:
            half_widths.append(0.0)
            continue
        xs = [point[0] for point in coordinates]
        half_widths.append((max(xs) - min(xs)) / 2.0)

    widths = np.asarray(half_widths)
    window = max(1, int(smoothing_window))
    if window > 1:
        if window % 2 == 0:
            window += 1
        padding = window // 2
        widths = np.convolve(
            np.pad(widths, padding, mode="edge"),
            np.ones(window) / window,
            mode="valid",
        )

    valid = widths > 1e-6
    z_values = z_values[valid]
    widths = widths[valid]
    left = [(center_x - width, z) for width, z in zip(widths, z_values)]
    right = [(center_x + width, z) for width, z in zip(widths[::-1], z_values[::-1])]
    symmetric = Polygon(left + right).buffer(0)
    if symmetric.is_empty:
        raise ValueError("Symmetry operation produced an empty section")
    return _largest_polygon(symmetric), center_x


def _largest_polygon(shape: Polygon | MultiPolygon) -> Polygon:
    if isinstance(shape, Polygon):
        return shape
    return max(shape.geoms, key=lambda polygon: polygon.area)


def _wire(points_xz: Iterable[tuple[float, float]], y: float) -> cq.Wire:
    vectors = [cq.Vector(float(x), y, float(z)) for x, z in points_xz]
    return cq.Wire.makePolygon(vectors, close=True)


def _extrude_polygon(polygon: Polygon, y0: float, height: float) -> cq.Shape:
    exterior = _wire(list(polygon.exterior.coords)[:-1], y0)
    holes = [_wire(list(ring.coords)[:-1], y0) for ring in polygon.interiors]
    return cq.Solid.extrudeLinear(exterior, holes, cq.Vector(0, height, 0))


def make_gauge(
    neck: Polygon,
    level_y: float,
    height: float,
    clearance: float,
    wall: float,
    rear_gap: float,
    point_count: int,
    edge_round: float,
) -> tuple[cq.Shape, Polygon, Polygon, float]:
    fitted = _resample_ring(_largest_polygon(neck.buffer(clearance)), point_count)
    outside = _resample_ring(_largest_polygon(fitted.buffer(wall)), point_count)
    annulus = outside.difference(fitted)

    center_x = fitted.centroid.x
    posterior_z = outside.bounds[1]
    gap_cut = box(
        center_x - rear_gap / 2.0,
        posterior_z - wall * 4.0,
        center_x + rear_gap / 2.0,
        fitted.centroid.y,
    )
    gauge_profile = _largest_polygon(annulus.difference(gap_cut))
    solid = _extrude_polygon(gauge_profile, level_y - height / 2.0, height)
    applied_edge_round = 0.0
    if edge_round > 0.0:
        # Round the skin-facing top and bottom rims while retaining straight
        # extrusion edges so the sectional gauge stays dimensionally legible.
        for radius in (edge_round, edge_round / 2.0, edge_round / 4.0):
            try:
                candidate = (
                    cq.Workplane(obj=solid)
                    .edges("not(|Y)")
                    .fillet(radius)
                    .val()
                )
                if not candidate.isValid() or len(candidate.Solids()) != 1:
                    continue
                solid = candidate
                applied_edge_round = radius
                break
            except Exception:
                continue
    return solid, fitted, outside, applied_edge_round


def _write_section_svg(
    output: Path,
    raw_neck: Polygon,
    symmetric_neck: Polygon,
    fitted: Polygon,
    outside: Polygon,
) -> None:
    polygons = [
        (raw_neck, "#a0aec0", "2 2"),
        (symmetric_neck, "#2d3748", ""),
        (fitted, "#2b6cb0", ""),
        (outside, "#c53030", ""),
    ]
    min_x = min(item.bounds[0] for item, _, _ in polygons)
    min_z = min(item.bounds[1] for item, _, _ in polygons)
    max_x = max(item.bounds[2] for item, _, _ in polygons)
    max_z = max(item.bounds[3] for item, _, _ in polygons)
    margin = 8.0
    width, height = max_x - min_x + 2 * margin, max_z - min_z + 2 * margin

    paths = []
    for polygon, color, dash in polygons:
        points = " ".join(
            f"{x - min_x + margin:.3f},{max_z - z + margin:.3f}"
            for x, z in polygon.exterior.coords
        )
        paths.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'stroke-dasharray="{dash}" stroke-width="0.8" '
            'vector-effect="non-scaling-stroke"/>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.3f} {height:.3f}">'
        '<rect width="100%" height="100%" fill="white"/>'
        + "".join(paths)
        + "</svg>\n"
    )
    output.write_text(svg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sectional TPU sleeve fit gauges.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "build" / "fit-gauges")
    parser.add_argument("--level", type=float, action="append", dest="levels")
    args = parser.parse_args()

    config = load_config(args.config)
    scan_path = resolve_project_path(config, config["scan"])
    report = inspect_binary_stl(scan_path, float(config["scale_to_mm"]))
    neck_config = config["neck"]
    gauge_config = config["fit_gauge"]
    levels = args.levels or neck_config["section_levels_y_mm"]
    args.output.mkdir(parents=True, exist_ok=True)

    manifest = {"scan": report, "config": config, "gauges": []}
    for level in levels:
        print(f"sectioning Y={level:.2f} mm ...", flush=True)
        segments = _section_segments(
            scan_path,
            report["triangle_count"],
            float(level),
            float(config["scale_to_mm"]),
        )
        neck = _neck_polygon(
            segments,
            (
                float(neck_config["expected_center_x_mm"]),
                float(neck_config["expected_center_z_mm"]),
            ),
            float(neck_config["section_search_radius_mm"]),
        )
        symmetry = neck_config["symmetry"]
        if symmetry["enabled"]:
            fitted_neck, symmetry_center_x = _symmetrize_polygon(
                neck,
                int(symmetry["samples"]),
                int(symmetry["smoothing_window"]),
            )
        else:
            fitted_neck, symmetry_center_x = neck, None
        solid, fitted, outside, applied_edge_round = make_gauge(
            fitted_neck,
            float(level),
            float(gauge_config["height_mm"]),
            float(gauge_config["clearance_mm"]),
            float(gauge_config["wall_thickness_mm"]),
            float(gauge_config["rear_gap_mm"]),
            int(gauge_config["contour_points"]),
            float(gauge_config["edge_round_mm"]),
        )

        stem = f"melissa-fit-gauge-y{level:+07.2f}".replace(".", "p")
        stl_path = args.output / f"{stem}.stl"
        step_path = args.output / f"{stem}.step"
        svg_path = args.output / f"{stem}-section.svg"
        # Preserve scan coordinates in STEP, but map scan Y to print Z so the
        # STL lands flat on a rim when opened in a conventional slicer.
        print_solid = solid.rotate((0, 0, 0), (1, 0, 0), 90.0)
        cq.exporters.export(
            print_solid,
            str(stl_path),
            tolerance=0.08,
            angularTolerance=0.15,
        )
        cq.exporters.export(solid, str(step_path))
        _write_section_svg(svg_path, neck, fitted_neck, fitted, outside)
        manifest["gauges"].append(
            {
                "level_y_mm": level,
                "source_section_area_mm2": neck.area,
                "symmetric_section_area_mm2": fitted_neck.area,
                "symmetry_center_x_mm": symmetry_center_x,
                "edge_round_mm_applied": applied_edge_round,
                "stl": str(stl_path),
                "stl_coordinate_system": "print-z-up",
                "step": str(step_path),
                "step_coordinate_system": "scan-y-up",
                "preview": str(svg_path),
            }
        )
        print(f"wrote {stl_path.name}")

    manifest["config"].pop("_config_path", None)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
