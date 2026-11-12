"""Smoothed outer surface of the inner sleeve, in the sleeve's local frame.

Every brace part is laid out on this profile, so it is rebuilt from the scan
the same way `full_sleeve` builds the sleeve itself.
"""

from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon

from .config import resolve_project_path
from .fit_gauges import _largest_polygon, _neck_polygon, _section_segments, _symmetrize_polygon
from .full_sleeve import _fit_neck_axis, _plane_basis, _project_polygon_to_plane, _smooth_containing_envelope
from .scan import inspect_binary_stl


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
