from __future__ import annotations

import cadquery as cq

from .cells import Block, Cell

MOUTH_CHAMFER = 0.8
RIB_WIDTH = 1.0
RIB_LENGTH = 12.0
RIB_START = 1.5        # below the mouth chamfer, so the cell is centred before it meets a rib
RIB_ROOT = 0.3         # rib sinks this far into the bore wall so the union fuses
RIB_ANGLES = (90.0, 210.0, 330.0)


def _rib(tip: float, root: float, top: float) -> cq.Workplane:
    """One crush rib, built pointing along +X from the hole axis, 45° lead at both ends."""
    lead = root - tip
    z1 = top - MOUTH_CHAMFER - RIB_START
    z0 = z1 - RIB_LENGTH
    profile = [(root, z0 - lead), (root, z1 + lead), (tip, z1), (tip, z0)]
    return (
        cq.Workplane("XZ")
        .polyline(profile)
        .close()
        .extrude(RIB_WIDTH / 2.0, both=True)
    )


def ribs(cell: Cell, squeeze: float, top: float, x: float, y: float) -> list[cq.Solid]:
    """Three ribs for a bore on the Z axis at (x, y) whose mouth is at z=top."""
    rib = _rib((cell.diameter - squeeze) / 2.0, cell.bore / 2.0 + RIB_ROOT, top)
    return [
        rib.rotate((0, 0, 0), (0, 0, 1), angle).translate((x, y, 0)).val()
        for angle in RIB_ANGLES
    ]


def mouth(cell: Cell, top: float, x: float, y: float) -> cq.Solid:
    r = cell.bore / 2.0
    return cq.Solid.makeCone(r, r + MOUTH_CHAMFER + 0.01, MOUTH_CHAMFER + 0.01,
                             cq.Vector(x, y, top - MOUTH_CHAMFER))


FLAT_RIB_OFFSETS = (-7.0, 7.0)   # two ribs per wide face of a 9V, either side of centre


def flat_ribs(block: Block, top: float, x: float, y: float) -> list[cq.Solid]:
    """Ribs on the two faces of a rectangular pocket that face +X and -X."""
    rib = _rib((block.across - block.squeeze) / 2.0, block.opening[0] / 2.0 + RIB_ROOT, top)
    return [
        rib.rotate((0, 0, 0), (0, 0, 1), angle).translate((x, y + dy, 0)).val()
        for angle in (0.0, 180.0) for dy in FLAT_RIB_OFFSETS
    ]


def rect_mouth(w: float, h: float, top: float, x: float, y: float) -> cq.Solid:
    c = MOUTH_CHAMFER + 0.01
    lo = cq.Sketch().rect(w, h).moved(cq.Location(cq.Vector(0, 0, top - MOUTH_CHAMFER)))
    hi = cq.Sketch().rect(w + 2 * c, h + 2 * c).moved(cq.Location(cq.Vector(0, 0, top + 0.01)))
    return cq.Workplane("XY").placeSketch(lo, hi).loft().translate((x, y, 0)).val()
