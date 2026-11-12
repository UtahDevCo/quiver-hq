from __future__ import annotations

import cadquery as cq

from .cells import Block, Cell, Hole, Slot
from .ribs import flat_ribs, mouth, rect_mouth, ribs

BORE_WALL = 2.0
SLOT_WALL = 1.6


def opening(hole: Hole) -> tuple[float, float]:
    """Width across the face and height up the face."""
    return (hole.bore, hole.bore) if isinstance(hole, Cell) else hole.opening


def wall(hole: Hole) -> float:
    return SLOT_WALL if isinstance(hole, Slot) else BORE_WALL


def cutter(hole: Hole, top: float, x: float, y: float) -> cq.Solid:
    if isinstance(hole, Cell):
        return cq.Solid.makeCylinder(hole.bore / 2.0, hole.depth + 1.0, cq.Vector(x, y, top - hole.depth))
    w, h = opening(hole)
    return cq.Solid.makeBox(w, h, hole.depth + 1.0, cq.Vector(x - w / 2.0, y - h / 2.0, top - hole.depth))


def chamfer(hole: Hole, top: float, x: float, y: float) -> cq.Solid | None:
    if isinstance(hole, Cell):
        return mouth(hole, top, x, y)
    if isinstance(hole, Block):
        return rect_mouth(*opening(hole), top, x, y)
    return None


def grip(hole: Hole, top: float, x: float, y: float) -> list[cq.Solid]:
    if isinstance(hole, Cell):
        return ribs(hole, hole.squeeze, top, x, y)
    if isinstance(hole, Block):
        return flat_ribs(hole, top, x, y)
    return []
