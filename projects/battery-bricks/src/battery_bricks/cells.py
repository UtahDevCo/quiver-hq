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
C_CELL = Cell("C", 26.2, 50.0, 0.6, 0.2, 33.0)   # not on the coupon; takes the AA squeeze


@dataclass(frozen=True)
class Block:
    """A 9V stood on its narrow edge: `across` faces the ribs, `tall` runs up the face."""
    name: str
    across: float
    tall: float
    length: float
    clearance: float
    squeeze: float
    depth: float

    @property
    def opening(self) -> tuple[float, float]:
        return self.across + self.clearance, self.tall + self.clearance


@dataclass(frozen=True)
class Slot:
    """A coin cell stood on edge in a thin slot."""
    name: str
    width: float
    tall: float
    length: float   # the coin's diameter, along the slot's depth
    depth: float

    @property
    def opening(self) -> tuple[float, float]:
        return self.width, self.tall


NINE_VOLT = Block("9V", 17.5, 26.5, 48.5, 0.6, 0.2, 30.0)
COIN = Slot("coin", 3.8, 20.6, 20.0, 14.0)    # CR2032 is 20 x 3.2; 6 mm stays out to pinch

Hole = Cell | Block | Slot
BY_NAME: dict[str, Hole] = {h.name: h for h in (*CELLS, C_CELL, NINE_VOLT, COIN)}
