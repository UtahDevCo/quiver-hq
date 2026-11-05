from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = PROJECT_ROOT / "build"


@dataclass(frozen=True)
class Cell:
    name: str
    diameter: float
    length: float
    clearance: float
    squeeze: float   # rib tips touch diameter - squeeze; picked from the fit coupon
    depth: float     # bore depth in a brick

    @property
    def bore(self) -> float:
        return self.diameter + self.clearance


# Nominal maximum diameters. Real cells run up to 0.4 mm under these, which is
# what the crush ribs take up. Squeezes come from the printed coupon: AAA row 2,
# AA row 2, 18650 row 1, and 21700 was tight even in row 1, so it opens 0.2 past it.
CELLS = (
    Cell("AAA", 10.5, 44.5, 0.6, 0.2, 30.0),
    Cell("AA", 14.5, 50.5, 0.6, 0.2, 33.0),
    Cell("18650", 18.4, 65.5, 0.8, 0.0, 40.0),
    Cell("21700", 21.2, 70.5, 0.8, -0.2, 40.0),
)
BY_NAME = {c.name: c for c in CELLS}
