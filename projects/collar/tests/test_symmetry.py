import unittest

from shapely.affinity import scale
from shapely.geometry import Polygon

from collar.fit_gauges import _symmetrize_polygon


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


if __name__ == "__main__":
    unittest.main()
