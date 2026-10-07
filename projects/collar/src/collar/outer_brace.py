from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import Polygon

from .config import DEFAULT_CONFIG, PROJECT_ROOT, load_config, resolve_project_path
from .fit_gauges import _largest_polygon, _neck_polygon, _section_segments, _symmetrize_polygon
from .full_sleeve import (
    _fit_neck_axis,
    _local_to_scan_matrix,
    _plane_basis,
    _project_polygon_to_plane,
    _smooth_containing_envelope,
    build_full_sleeve,
)
from .scan import inspect_binary_stl


def _wedge(center: tuple[float, float], start_deg: float, end_deg: float, radius: float) -> Polygon:
    """Return a counter-clockwise polar wedge, allowing angles above 360."""
    if end_deg <= start_deg or radius <= 0.0:
        raise ValueError("Brace wedge requires increasing angles and positive radius")
    count = max(8, int(math.ceil((end_deg - start_deg) / 2.0)))
    angles = np.linspace(math.radians(start_deg), math.radians(end_deg), count + 1)
    cx, cz = center
    return Polygon(
        [(cx, cz)]
        + [(cx + radius * math.cos(a), cz + radius * math.sin(a)) for a in angles]
    )


def _extrude_polygon_xz(polygon: Polygon, height: float) -> cq.Shape:
    """Extrude a Shapely polygon symmetrically along local neck-axis Y."""
    polygon = _largest_polygon(polygon.buffer(0))

    def wire(coords) -> cq.Wire:
        return cq.Wire.makePolygon(
            [cq.Vector(float(x), -height / 2.0, float(z)) for x, z in list(coords)[:-1]],
            close=True,
        )

    exterior = wire(polygon.exterior.coords)
    holes = [wire(interior.coords) for interior in polygon.interiors]
    return cq.Solid.extrudeLinear(exterior, holes, cq.Vector(0.0, height, 0.0))


def _reference_outer_profile(config: dict) -> tuple[Polygon, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Rebuild the sleeve waist profile and its registered local frame."""
    scan_path = resolve_project_path(config, config["scan"])
    scale = float(config["scale_to_mm"])
    report = inspect_binary_stl(scan_path, scale)
    neck = config["neck"]
    sleeve = config["full_sleeve"]
    expected = (float(neck["expected_center_x_mm"]), float(neck["expected_center_z_mm"]))
    radius = float(neck["section_search_radius_mm"])
    reference_level = float(sleeve["reference_level_y_mm"])
    raw = _neck_polygon(
        _section_segments(scan_path, report["triangle_count"], reference_level, scale),
        expected,
        radius,
    )
    symmetry = neck["symmetry"]
    if symmetry["enabled"]:
        reference, center_x = _symmetrize_polygon(
            raw, int(symmetry["samples"]), int(symmetry["smoothing_window"])
        )
    else:
        reference = raw
        center_x = (raw.bounds[0] + raw.bounds[2]) / 2.0

    alignment = sleeve["alignment"]
    centers: list[tuple[float, float, float]] = []
    if alignment["enabled"]:
        for value in alignment["section_levels_y_mm"]:
            level = float(value)
            section = _neck_polygon(
                _section_segments(scan_path, report["triangle_count"], level, scale),
                expected,
                radius,
            )
            centers.append((float(section.centroid.x), level, float(section.centroid.y)))
    axis = _fit_neck_axis(centers) if alignment["enabled"] else np.asarray((0.0, 1.0, 0.0))
    center = np.asarray((center_x, reference_level, reference.centroid.y), dtype=float)
    local_x, local_z = _plane_basis(axis)
    local_reference = _project_polygon_to_plane(
        reference, reference_level, center, local_x, local_z
    )
    required_outer = _largest_polygon(
        local_reference.buffer(float(sleeve["clearance_mm"]) + float(sleeve["wall_thickness_mm"]))
    )
    outer_config = sleeve["outer_interface"]
    outer, _ = _smooth_containing_envelope(
        required_outer, int(outer_config["samples"]), int(outer_config["harmonics"])
    )
    return outer, center, local_x, axis, local_z


def _segment_ranges(count: int, rear_opening_deg: float, gap_deg: float) -> list[tuple[float, float]]:
    """Divide the non-posterior circumference into separated angular ranges."""
    if count < 3 or not 0.0 < rear_opening_deg < 180.0 or gap_deg < 0.0:
        raise ValueError("Invalid segmented-brace angular configuration")
    start = -90.0 + rear_opening_deg / 2.0
    cell = (360.0 - rear_opening_deg) / count
    if gap_deg >= cell:
        raise ValueError("Brace segment gap must be smaller than each segment")
    return [
        (start + i * cell + gap_deg / 2.0, start + (i + 1) * cell - gap_deg / 2.0)
        for i in range(count)
    ]


def _ring_between(profile: Polygon, inner: float, outer: float) -> Polygon:
    if outer <= inner:
        raise ValueError("Ring outer offset must exceed inner offset")
    return _largest_polygon(profile.buffer(outer).difference(profile.buffer(inner)))


def build_outer_brace(config: dict) -> tuple[cq.Shape, list[cq.Shape], cq.Shape, cq.Shape, dict]:
    """Build a measured-hardware packaging concept around the fitted waist."""
    brace = config["outer_brace"]
    profile, center, local_x, axis, local_z = _reference_outer_profile(config)
    cx, cz = profile.centroid.coords[0]
    wedge_radius = max(math.hypot(x - cx, z - cz) for x, z in profile.exterior.coords) + 40.0

    clearance = float(brace["sleeve_clearance_mm"])
    base = float(brace["segment_base_thickness_mm"])
    strap_width = float(brace["strap_width_mm"])
    strap_thickness = float(brace["strap_thickness_mm"])
    vertical_clearance = float(brace["strap_vertical_clearance_mm"])
    radial_clearance = float(brace["strap_radial_clearance_mm"])
    wall = float(brace["guide_wall_mm"])
    channel_height = strap_width + 2.0 * vertical_clearance
    minimum_height = channel_height + 2.0 * wall
    segment_height = float(brace["segment_height_mm"])
    if segment_height < minimum_height:
        raise ValueError(
            f"Brace segment height must be at least {minimum_height:.2f} mm"
        )
    strap_inner = clearance + base + radial_clearance
    strap_outer = strap_inner + strap_thickness
    cap_inner = strap_outer + radial_clearance
    cap_outer = cap_inner + wall

    base_ring = _ring_between(profile, clearance, clearance + base)
    cap_middle = (cap_inner + cap_outer) / 2.0
    inner_cap_ring = _ring_between(profile, cap_inner, cap_middle)
    outer_cap_ring = _ring_between(profile, cap_middle, cap_outer)
    rail_ring = _ring_between(profile, clearance + base, cap_outer)
    ranges = _segment_ranges(
        int(brace["segment_count"]),
        float(brace["rear_opening_angle_deg"]),
        float(brace["segment_gap_angle_deg"]),
    )
    mean_radius = profile.exterior.length / (2.0 * math.pi)
    overlap_deg = math.degrees(float(brace["lap_overlap_mm"]) / mean_radius)
    segments: list[cq.Shape] = []
    for index, (start, end) in enumerate(ranges):
        sector = _wedge((cx, cz), start, end, wedge_radius)
        base_piece = _extrude_polygon_xz(
            base_ring.intersection(sector), segment_height
        )
        # Complementary radial half-laps bridge every visible strap gap. The
        # clockwise segment slides beneath the preceding segment's outer tongue.
        inner_start = start - overlap_deg if index > 0 else start
        outer_end = end + overlap_deg if index < len(ranges) - 1 else end
        inner_sector = _wedge((cx, cz), inner_start, end, wedge_radius)
        outer_sector = _wedge((cx, cz), start, outer_end, wedge_radius)
        cap_piece = _extrude_polygon_xz(
            inner_cap_ring.intersection(inner_sector), segment_height
        ).fuse(
            _extrude_polygon_xz(
                outer_cap_ring.intersection(outer_sector), segment_height
            )
        )
        rails = rail_ring.intersection(sector)
        lower = _extrude_polygon_xz(rails, wall).translate(
            (0.0, -(channel_height + wall) / 2.0, 0.0)
        )
        upper = _extrude_polygon_xz(rails, wall).translate(
            (0.0, (channel_height + wall) / 2.0, 0.0)
        )
        segments.append(base_piece.fuse(cap_piece).fuse(lower).fuse(upper))

    assembly = cq.Compound.makeCompound(segments)
    rear_opening = float(brace["rear_opening_angle_deg"])
    strap_sector = _wedge(
        (cx, cz),
        -90.0 + rear_opening / 2.0,
        270.0 - rear_opening / 2.0,
        wedge_radius,
    )
    strap = _extrude_polygon_xz(
        _ring_between(profile, strap_inner, strap_outer).intersection(strap_sector),
        strap_width,
    )

    buckle_length = float(brace["buckle_length_mm"])
    buckle_width = float(brace["buckle_width_mm"])
    buckle_depth = float(brace["buckle_depth_mm"])
    buckle = cq.Solid.makeBox(
        buckle_length,
        buckle_width,
        buckle_depth,
        cq.Vector(
            cx - buckle_length / 2.0,
            -buckle_width / 2.0,
            profile.bounds[1] - buckle_depth - clearance,
        ),
    )

    transform = _local_to_scan_matrix(center, local_x, axis, local_z)
    registered_segments = [part.transformGeometry(transform) for part in segments]
    metadata = {
        "purpose": "measured-hardware concept; not yet approved for wear",
        "segment_count": len(segments),
        "segment_height_mm": segment_height,
        "lap_overlap_mm": float(brace["lap_overlap_mm"]),
        "lap_overlap_angle_deg": overlap_deg,
        "sleeve_clearance_mm": clearance,
        "strap": {
            "width_mm": strap_width,
            "thickness_mm": strap_thickness,
            "guide_internal_width_mm": channel_height,
            "guide_internal_depth_mm": strap_thickness + 2.0 * radial_clearance,
            "measured_ten_tooth_span_mm": float(brace["ten_tooth_span_mm"]),
        },
        "buckle_envelope_mm": [buckle_length, buckle_width, buckle_depth],
        "rear_opening_angle_deg": rear_opening,
        "segment_gap_angle_deg": float(brace["segment_gap_angle_deg"]),
    }
    return (
        cq.Compound.makeCompound(registered_segments),
        registered_segments,
        strap.transformGeometry(transform),
        buckle.transformGeometry(transform),
        metadata,
    )


def _mesh(shape: cq.Shape, path: Path) -> trimesh.Trimesh:
    cq.exporters.export(shape, str(path), tolerance=0.08, angularTolerance=0.15)
    return trimesh.load_mesh(path, process=False)


def _write_preview(output: Path, items: list[tuple[trimesh.Trimesh, tuple[float, float, float], float]]) -> None:
    import vtk

    from .fit_scene import _vtk_actor

    bounds = np.vstack([mesh.bounds for mesh, _, _ in items])
    center = (bounds.min(axis=0) + bounds.max(axis=0)) / 2.0
    views = [
        ("Front", np.asarray((0.0, 0.0, 1.0))),
        ("Left", np.asarray((-1.0, 0.0, 0.0))),
        ("Rear ratchet", np.asarray((0.0, 0.0, -1.0))),
        ("Isometric", np.asarray((1.0, 0.35, -1.0))),
    ]
    window = vtk.vtkRenderWindow()
    window.SetSize(2200, 650)
    window.SetOffScreenRendering(1)
    for index, (title, direction) in enumerate(views):
        renderer = vtk.vtkRenderer()
        renderer.SetViewport(index / 4.0, 0.0, (index + 1) / 4.0, 1.0)
        renderer.SetBackground(0.965, 0.972, 0.98)
        for mesh, color, opacity in items:
            renderer.AddActor(_vtk_actor(mesh, color, opacity))
        direction /= np.linalg.norm(direction)
        camera = renderer.GetActiveCamera()
        camera.SetFocalPoint(*center)
        camera.SetPosition(*(center + direction * 1000.0))
        camera.SetViewUp(0.0, 1.0, 0.0)
        camera.ParallelProjectionOn()
        renderer.ResetCamera()
        camera.Zoom(1.05)
        label = vtk.vtkTextActor()
        label.SetInput(title)
        label.GetTextProperty().SetFontSize(24)
        label.GetTextProperty().SetColor(0.08, 0.10, 0.14)
        label.GetTextProperty().SetJustificationToCentered()
        label.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        label.SetPosition(0.5, 0.94)
        renderer.AddViewProp(label)
        window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGBA()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Melissa's segmented outer-brace concept.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "build" / "outer-brace")
    args = parser.parse_args()
    config = load_config(args.config)
    sleeve, _ = build_full_sleeve(config)
    brace, segments, strap, buckle, metadata = build_outer_brace(config)
    args.output.mkdir(parents=True, exist_ok=True)
    sleeve_mesh = _mesh(sleeve, args.output / "melissa-inner-sleeve-reference.stl")
    brace_mesh = _mesh(brace, args.output / "melissa-segmented-brace-concept.stl")
    strap_mesh = _mesh(strap, args.output / "measured-strap-envelope.stl")
    buckle_mesh = _mesh(buckle, args.output / "measured-buckle-envelope.stl")
    for index, segment in enumerate(segments, start=1):
        cq.exporters.export(segment, str(args.output / f"brace-segment-{index:02d}.stl"))

    items = [
        (sleeve_mesh, (0.10, 0.34, 0.68), 0.70),
        (brace_mesh, (0.12, 0.13, 0.15), 1.0),
        (strap_mesh, (0.88, 0.48, 0.06), 1.0),
        (buckle_mesh, (0.55, 0.58, 0.62), 1.0),
    ]
    scene = trimesh.Scene()
    for name, (mesh, color, opacity) in zip(
        ("Sleeve", "Brace segments", "Ratchet strap", "Buckle envelope"), items
    ):
        rgba = np.asarray((*[round(v * 255) for v in color], round(opacity * 255)), dtype=np.uint8)
        mesh.visual.face_colors = np.tile(rgba, (len(mesh.faces), 1))
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    scene.export(args.output / "melissa-ratchet-brace-concept.glb")
    _write_preview(args.output / "preview.png", items)
    metadata["artifacts"] = {
        "preview": str(args.output / "preview.png"),
        "scene_glb": str(args.output / "melissa-ratchet-brace-concept.glb"),
        "brace_concept_stl": str(args.output / "melissa-segmented-brace-concept.stl"),
    }
    (args.output / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"wrote {args.output / 'preview.png'}")


if __name__ == "__main__":
    main()
