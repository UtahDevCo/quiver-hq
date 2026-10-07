import unittest

import numpy as np
from shapely.affinity import scale
from shapely.geometry import Polygon

from collar.fit_gauges import _symmetrize_polygon
from collar.fit_scene import _expanded_bounds, _vertex_cluster_proxy
from collar.full_sleeve import (
    _canonical_points,
    _fit_neck_axis,
    _fourier_smooth_polygon,
    _hourglass_sections,
    _plane_basis,
    _smooth_containing_envelope,
)
from collar.outer_brace import _segment_ranges


class SymmetryTests(unittest.TestCase):
    def test_section_is_exactly_mirrored_about_reported_center(self) -> None:
        asymmetric = Polygon(
            [(-3, -2), (4, -2), (5, 0), (3, 2), (-2, 2), (-4, 0)]
        )

        symmetric, center_x = _symmetrize_polygon(
            asymmetric,
            samples=101,
            smoothing_window=5,
        )
        mirrored = scale(symmetric, xfact=-1, yfact=1, origin=(center_x, 0))

        self.assertTrue(symmetric.is_valid)
        self.assertGreater(symmetric.area, 0)
        self.assertAlmostEqual(symmetric.symmetric_difference(mirrored).area, 0.0)

    def test_loft_sampling_starts_at_posterior_center(self) -> None:
        rectangle = Polygon([(-3, -2), (3, -2), (3, 4), (-3, 4)])

        points = _canonical_points(rectangle, center_x=0.0, point_count=12)

        self.assertAlmostEqual(points[0][0], 0.0)
        self.assertAlmostEqual(points[0][1], -2.0)
        self.assertEqual(len(points), 12)

    def test_hourglass_centers_fitted_core_and_uses_shallow_flares(self) -> None:
        stations = _hourglass_sections(
            reference_level=0.0,
            core_height=38.0,
            flare_height=18.0,
            flare_outset=8.0,
            flare_steps=8,
        )

        self.assertAlmostEqual(stations[0][0], -37.0)
        self.assertAlmostEqual(stations[0][1], 8.0)
        self.assertIn((-19.0, 0.0), stations)
        self.assertIn((19.0, 0.0), stations)
        self.assertAlmostEqual(stations[-1][0], 37.0)
        self.assertAlmostEqual(stations[-1][1], 8.0)

    def test_fit_scene_crop_expands_each_axis(self) -> None:
        minimum, maximum = _expanded_bounds(
            np.asarray((-2.0, -3.0, -4.0)),
            np.asarray((2.0, 3.0, 4.0)),
            np.asarray((1.0, 2.0, 3.0)),
        )

        np.testing.assert_allclose(minimum, (-3.0, -5.0, -7.0))
        np.testing.assert_allclose(maximum, (3.0, 5.0, 7.0))

    def test_fit_scene_proxy_removes_clustered_degenerate_faces(self) -> None:
        triangles = np.asarray(
            [
                ((0.0, 0.0, 0.0), (0.1, 0.0, 0.0), (0.0, 0.1, 0.0)),
                ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (0.0, 2.0, 0.0)),
            ]
        )

        proxy = _vertex_cluster_proxy(triangles, voxel_mm=1.0)

        self.assertEqual(len(proxy.faces), 1)
        self.assertEqual(len(proxy.vertices), 3)

    def test_neck_axis_fit_and_plane_basis_are_orthonormal(self) -> None:
        centers = [
            (-1.0, -10.0, -8.0),
            (0.0, 0.0, 0.0),
            (1.0, 10.0, 8.0),
        ]

        axis = _fit_neck_axis(centers)
        local_x, local_z = _plane_basis(axis)

        self.assertGreater(axis[1], 0.0)
        self.assertAlmostEqual(float(np.linalg.norm(axis)), 1.0)
        self.assertAlmostEqual(float(np.dot(axis, local_x)), 0.0)
        self.assertAlmostEqual(float(np.dot(axis, local_z)), 0.0)
        self.assertAlmostEqual(float(np.dot(local_x, local_z)), 0.0)

    def test_smooth_outer_interface_contains_required_wall(self) -> None:
        lumpy = Polygon(
            [
                (-4.0, -3.0),
                (-1.0, -3.4),
                (0.0, -3.0),
                (1.0, -3.4),
                (4.0, -3.0),
                (4.2, 3.0),
                (0.0, 3.2),
                (-4.2, 3.0),
            ]
        )

        smoothed = _fourier_smooth_polygon(lumpy, point_count=96, harmonics=4)
        envelope, expansion = _smooth_containing_envelope(
            lumpy,
            point_count=96,
            harmonics=4,
        )

        self.assertTrue(smoothed.is_valid)
        self.assertTrue(envelope.buffer(1e-6).covers(lumpy))
        self.assertGreaterEqual(expansion, 0.0)

    def test_segment_ranges_leave_rear_opening_and_even_cells(self) -> None:
        ranges = _segment_ranges(8, rear_opening_deg=34.0, gap_deg=3.0)

        self.assertEqual(len(ranges), 8)
        self.assertAlmostEqual(ranges[0][0], -71.5)
        self.assertAlmostEqual(ranges[-1][1], 251.5)
        self.assertTrue(all(end > start for start, end in ranges))


if __name__ == "__main__":
    unittest.main()
