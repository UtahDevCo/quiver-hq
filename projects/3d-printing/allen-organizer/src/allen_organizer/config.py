from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "inventory.json"
BUILD_DIR = PROJECT_ROOT / "build"


@dataclass(frozen=True)
class Hole:
    label: str
    key_mm: float
    depth_mm: float
    reserved: bool

    def bore_mm(self, clearance_mm: float) -> float:
        return self.key_mm + clearance_mm


@dataclass(frozen=True)
class Tier:
    name: str
    rise_mm: float
    holes: tuple[Hole, ...]


@dataclass(frozen=True)
class Params:
    clearance_mm: float
    pitch_mm: float
    row_depth_mm: float
    row_gap_mm: float
    floor_mm: float
    back_tier_rise_mm: float
    chamfer_mm: float
    min_wall_mm: float


@dataclass(frozen=True)
class Inventory:
    params: Params
    tiers: tuple[Tier, ...]
    spares: dict[str, Any]
    tray: dict[str, Any]


def _hole(raw: dict[str, Any]) -> Hole:
    return Hole(
        label=str(raw["label"]),
        key_mm=float(raw["key_mm"]),
        depth_mm=float(raw["depth_mm"]),
        reserved=bool(raw.get("reserved", False)),
    )


def load_inventory(path: Path | None = None) -> Inventory:
    config_path = (path or DEFAULT_CONFIG).resolve()
    raw = json.loads(config_path.read_text())
    params = Params(**{k: float(v) for k, v in raw["params"].items()})
    tiers = tuple(
        Tier(
            name=str(t["name"]),
            rise_mm=float(t.get("rise_mm", 0.0)),
            holes=tuple(_hole(h) for h in t["holes"]),
        )
        for t in raw["tiers"]
    )
    return Inventory(
        params=params,
        tiers=tiers,
        spares=raw.get("spares", {}),
        tray=raw.get("tray", {}),
    )
