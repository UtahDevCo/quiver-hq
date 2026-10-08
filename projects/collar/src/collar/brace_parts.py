"""Printable cord-strung brace: anchor, five segments, dial pod and its lid.

Joints.  Neighbouring parts bear on each other along a vertical joint line
just inside the outer surface, where the two cords run.  Each end face is two
planes meeting on that line: the inner face leaves a small wedge that closes
flush when the brace is squeezed, and the outer face is cut back so the joint
can open about 30 degrees for putting the collar on.

Seam.  The chain's length is fixed by the parts and cords, so the brace only
shrinks by the seam closing.  Wrapped loosely the seam is about 13 mm open;
about 5 mm brings the brace onto the sleeve and the last 8 mm is the squeeze.
The pod's and anchor's seam faces are cut so they meet flush at that point:
the hard minimum-circumference stop.  Joint wedges allow 30 percent more than
their share of the squeeze, so the seam stop always decides.

Cords.  Two cords (4 mm paracord) run in tunnels from a knot pocket in the
anchor, through all five segments, to a knot pocket at the pod's trailing end.
Both pockets open on the inner face, against the sleeve.

Lace.  The dial's lace loop leaves the pod through its windows at the seam
face and is caught on the anchor's outer face: a straight slot from the seam
face to a round pocket for a knot tied in the loop.  Both are narrow at the
surface and wider underneath, so the lace and knot press in and stay.  Nothing is threaded, so with the dial popped the
knot lifts out and the collar opens fully.

Everything is built in the build frame (profile in XY, neck axis on Z), which
is also the upright print orientation.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np

from . import dial_pod
from .config import DEFAULT_CONFIG, PROJECT_ROOT, load_config
from .cord_brace import (
    BAND_HEIGHT_MM,
    EDGE_ROUND_MM,
    POD_EDGE_ROUND_MM,
    POD_STANDOFF_MM,
    SEGMENT_COUNT,
    SEGMENT_CROWN_MM,
    SEGMENT_DOME_WALL_MM,
    SLEEVE_CLEARANCE_MM,
    WALL_MM,
    _barrel,
    _layout,
    _ray_hit,
    _ring,
    _rounded,
    _to_local,
    _wedge,
)
from .sleeve_profile import _reference_outer_profile


CHAIN = ["anchor"] + [f"segment-{i + 1}" for i in range(SEGMENT_COUNT)] + ["dial-pod"]
FIXED_PART = "segment-3"

OUTER_EDGE = SLEEVE_CLEARANCE_MM + WALL_MM  # outer surface at part ends
JOINT_INSET_MM = 3.5  # joint line and cord centres below the outer edge
JOINT_OFFSET = OUTER_EDGE - JOINT_INSET_MM
MARGIN_DEG = 3.0
STOP_SHARE = 1.3  # joint wedges allow this multiple of their squeeze share
RELIEF_DEG = 30.0  # how far each joint can open

CORD_HEIGHTS_MM = (12.0, -12.0)
CORD_TUNNEL_MM = 4.6  # 4 mm paracord
KNOT_POCKET_MM = 7.0  # pocket width
KNOT_POCKET_PAST_CORD_MM = 2.5  # pocket reaches |z| = 14.5, 1 mm inside the edge round
KNOT_POCKET_INNER_Z_MM = 5.0  # and runs toward mid-height down to |z| = 5
ANCHOR_KNOT_FROM_JOINT_MM = 12.0
ANCHOR_KNOT_CHANNEL_MM = 1.5 * KNOT_POCKET_MM  # one channel for a square knot joining both cords
LABEL_DEPTH_MM = 0.6  # engraved into the inner face
LABEL_SIZE_MM = 7.0
LABELS = {"anchor": "A", **{f"segment-{i + 1}": str(i + 1) for i in range(SEGMENT_COUNT)}, "dial-pod": "P"}
LABEL_U_MM = {"anchor": 6.5}  # from the seam face; other parts are labelled mid-arc
LABEL_Z_MM = {"anchor": -11.0}  # below the knot pocket; others at mid-height
POD_KNOT_FROM_END_MM = 5.5

LACE_FACE_V_MM = 12.5  # where the strands leave the pod's windows
LACE_SLOT_U_MM = (-3.0,)  # straight slot starts past the seam face
LACE_SLOT_HEIGHT_MM = 3.8  # doubled lace is 3.2 mm side by side, plus clearance and sag
LACE_SLOT_DEPTH_MM = 3.0  # along the outward normal; the strands sit one behind the other
KNOT_CENTRE_U_MM = 13.5
KNOT_POCKET_DIA_MM = 10.0  # the knot in the doubled lace measures 8.45 mm
KNOT_FLOOR_OFFSET = SLEEVE_CLEARANCE_MM + 2.0  # 2 mm floor under the knot, about 7 mm deep


def _rot(v: np.ndarray, degrees: float) -> np.ndarray:
    a = math.radians(degrees)
    return np.array([v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a)])


def _surface_point(profile, offset: float, angle: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Point on an offset of the sleeve profile with its outward normal and CCW tangent."""
    p = _ray_hit(profile, offset, angle)
    a, b = _ray_hit(profile, offset, angle - 0.3), _ray_hit(profile, offset, angle + 0.3)
    t = (b - a) / np.linalg.norm(b - a)
    n = np.array([t[1], -t[0]])
    if n @ p < 0:
        n = -n
    return p, n, t


class Kinematics:
    """Rigid 2D motion of the chain, every joint turned by the same angle."""

    def __init__(self, pivots: list[np.ndarray]) -> None:
        self.pivots = pivots
        self.fixed = CHAIN.index(FIXED_PART)
        self.open_sign = 1.0

    def steps(self, part: str, angle: float) -> list[tuple[np.ndarray, float]]:
        """Rotations (pivot, degrees CCW) to apply in order to points on `part`."""
        i = CHAIN.index(part)
        a = self.open_sign * angle
        if i > self.fixed:
            return [(self.pivots[j], a) for j in range(i - 1, self.fixed - 1, -1)]
        if i < self.fixed:
            return [(self.pivots[j], -a) for j in range(i, self.fixed)]
        return []

    def move(self, point: np.ndarray, part: str, angle: float) -> np.ndarray:
        for pivot, degrees in self.steps(part, angle):
            point = pivot + _rot(point - pivot, degrees)
        return point

    def move_shape(self, shape: cq.Shape, part: str, angle: float) -> cq.Shape:
        for pivot, degrees in self.steps(part, angle):
            shape = shape.rotate(
                cq.Vector(float(pivot[0]), float(pivot[1]), 0),
                cq.Vector(float(pivot[0]), float(pivot[1]), 1),
                degrees,
            )
        return shape


def _halfspace(point: np.ndarray, normal: np.ndarray, keep_negative: bool) -> cq.Workplane:
    """Big block on the +normal side of a vertical plane (the side to cut away)."""
    n = normal / np.linalg.norm(normal)
    plane = cq.Plane(
        origin=cq.Vector(float(point[0]), float(point[1]), 0),
        xDir=cq.Vector(float(-n[1]), float(n[0]), 0),
        normal=cq.Vector(float(n[0]), float(n[1]), 0),
    )
    block = cq.Workplane(plane).rect(600, 200).extrude(300)
    if not keep_negative:
        block = cq.Workplane(plane).rect(600, 200).extrude(-300)
    return block


def _joint_cutter(pivot: np.ndarray, normal: np.ndarray, tangent: np.ndarray, side: int, wedge_deg: float) -> cq.Workplane:
    """Region to remove from the part on `side` (+1: CCW side of the joint)."""
    length = 40.0
    d_in = _rot(-normal, -side * wedge_deg / 2)
    d_out = _rot(normal, side * RELIEF_DEG / 2)
    away = -side * tangent * 2 * length
    points = [pivot, pivot + d_out * length, pivot + d_out * length + away, pivot + d_in * length + away, pivot + d_in * length]
    return (
        cq.Workplane("XY")
        .workplane(offset=-60)
        .polyline([(float(x), float(y)) for x, y in points])
        .close()
        .extrude(120)
    )


def _sweep_tube(points: list[cq.Vector], diameter: float) -> cq.Workplane:
    path = cq.Wire.assembleEdges([cq.Edge.makeSpline(points)])
    tangent = (points[1] - points[0]).normalized()
    reference = cq.Vector(0, 0, 1) if abs(tangent.z) < 0.9 else cq.Vector(1, 0, 0)
    plane = cq.Plane(origin=points[0], xDir=reference.cross(tangent).normalized(), normal=tangent)
    return cq.Workplane(plane).circle(diameter / 2).sweep(cq.Workplane().add(path))


def _knot_pockets(
    profile, angle: float, inner_offset: float, outer_offset: float, width: float = KNOT_POCKET_MM, joined: bool = False
) -> cq.Workplane:
    """One pocket per cord, opening on the inner face and meeting the tunnel.

    Each is a short slot centred on its cord and stretched toward mid-height,
    so a stopper knot fits without breaking through the top or bottom edge.
    """
    p, n, _ = _surface_point(profile, inner_offset - 1.0, angle)
    depth = outer_offset - inner_offset + 1.0
    reach = max(abs(h) for h in CORD_HEIGHTS_MM) + KNOT_POCKET_PAST_CORD_MM
    if joined:  # one channel across both cords, through mid-height
        plane = cq.Plane(
            origin=cq.Vector(float(p[0]), float(p[1]), 0.0),
            xDir=cq.Vector(0, 0, 1),
            normal=cq.Vector(float(n[0]), float(n[1]), 0),
        )
        return cq.Workplane(plane).slot2D(2 * reach, width).extrude(depth)
    pockets = None
    for height in CORD_HEIGHTS_MM:
        # One stadium-shaped cut per cord, from just past the cord toward
        # mid-height.  It must stop short of the 2.5 mm edge round: on the
        # 36 mm anchor a pocket touching that boundary made the inner face
        # unmeshable (and two overlapping cylinders were worse).
        outer = abs(height) + KNOT_POCKET_PAST_CORD_MM
        inner = KNOT_POCKET_INNER_Z_MM
        centre = math.copysign((outer + inner) / 2, height)
        plane = cq.Plane(
            origin=cq.Vector(float(p[0]), float(p[1]), float(centre)),
            xDir=cq.Vector(0, 0, 1),
            normal=cq.Vector(float(n[0]), float(n[1]), 0),
        )
        piece = cq.Workplane(plane).slot2D(outer - inner, width).extrude(depth)
        pockets = piece if pockets is None else pockets.union(piece)
    return pockets


def _arc_angle(profile, angle: float, arc_mm: float, offset: float) -> float:
    radius = float(np.linalg.norm(_ray_hit(profile, offset, angle)))
    return angle + math.degrees(arc_mm / radius)


def _lace_slot(profile, anchor: cq.Shape, u_angle) -> cq.Workplane:
    """Lace slot along the anchor's outer face, from past the seam face to the
    knot pocket.

    The anchor prints upright and the slot is open at both ends, so a flat
    ceiling would print in mid-air.  The slot is a straight channel sloping
    down into the part at 45 degrees: both faces print without support, and
    the doubled lace sits one strand behind the other along the diagonal.  It
    follows the domed outer face so its depth stays constant.
    """

    def surface(u: float) -> float:
        lo, hi = JOINT_OFFSET, OUTER_EDGE + SEGMENT_DOME_WALL_MM
        for _ in range(30):
            mid = (lo + hi) / 2
            q = _ray_hit(profile, mid, u_angle(u))
            lo, hi = (mid, hi) if anchor.isInside(cq.Vector(float(q[0]), float(q[1]), 0.0)) else (lo, mid)
        return lo

    first = 1.0  # sample inside the part, then carry the depth out past the seam face
    us = np.linspace(LACE_SLOT_U_MM[0], KNOT_CENTRE_U_MM, 12)
    pts = []
    for u in us:
        q = _ray_hit(profile, surface(max(u, first)), u_angle(u))
        pts.append(cq.Vector(float(q[0]), float(q[1]), 0.0))
    path = cq.Wire.assembleEdges([cq.Edge.makeSpline(pts)])

    tangent = (pts[1] - pts[0]).normalized()
    _, n0, _ = _surface_point(profile, JOINT_OFFSET, u_angle(us[0]))
    up = np.array([0.0, 0.0, 1.0])
    flip = 1.0 if np.cross([tangent.x, tangent.y, 0.0], up) @ [n0[0], n0[1], 0.0] > 0 else -1.0
    plane = cq.Plane(origin=pts[0], xDir=cq.Vector(0, 0, flip), normal=tangent)
    half, depth = LACE_SLOT_HEIGHT_MM / 2, LACE_SLOT_DEPTH_MM
    out = SEGMENT_DOME_WALL_MM  # well past the surface
    section = [  # (v up in the print, outward from the surface); both long faces at 45 degrees
        (-half - depth, -depth), (half - depth, -depth), (half + out, out), (-half + out, out),
    ]
    profile_wp = cq.Workplane(plane).polyline([(flip * v, d) for v, d in section]).close()
    return profile_wp.sweep(cq.Workplane().add(path), isFrenet=False)


def _label(profile, angle: float, inner_offset: float, text: str, z: float = 0.0) -> cq.Workplane:
    """Text engraved into an inner face, upright and readable from inside the ring."""
    p, n, _ = _surface_point(profile, inner_offset + LABEL_DEPTH_MM, angle)
    inward = cq.Vector(float(-n[0]), float(-n[1]), 0)
    right = cq.Vector(float(n[0]), float(n[1]), 0).cross(cq.Vector(0, 0, 1))
    plane = cq.Plane(origin=cq.Vector(float(p[0]), float(p[1]), z), xDir=right, normal=inward)
    return cq.Workplane(plane).text(text, LABEL_SIZE_MM, LABEL_DEPTH_MM + 1.0, combine=False, kind="bold")


def build(config: dict) -> dict:
    profile, *_ = _reference_outer_profile(config)
    ranges = _layout(profile)

    joints = []
    for left, right in zip(CHAIN, CHAIN[1:]):
        gap = (ranges[left][1] + ranges[right][0]) / 2
        pivot, normal, tangent = _surface_point(profile, JOINT_OFFSET, gap)
        joints.append({"between": (left, right), "angle": gap, "pivot": pivot, "normal": normal, "tangent": tangent})
    kin = Kinematics([j["pivot"] for j in joints])

    # Opening direction: the sign that spreads the seam.
    pod_corner = _ray_hit(profile, OUTER_EDGE, ranges["dial-pod"][1])
    anchor_corner = _ray_hit(profile, OUTER_EDGE, ranges["anchor"][0])
    seam_mid = (ranges["dial-pod"][1] + ranges["anchor"][0] + 360.0) / 2
    _, _, seam_t = _surface_point(profile, OUTER_EDGE, seam_mid)

    def seam_gap(angle: float) -> float:
        a = kin.move(anchor_corner, "anchor", angle)
        b = kin.move(pod_corner, "dial-pod", angle)
        return float((a - b) @ seam_t)

    kin.open_sign = 1.0 if seam_gap(5.0) > seam_gap(-5.0) else -1.0
    lo, hi = -6.0, 0.0  # closing is negative
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if seam_gap(mid) < 0 else (lo, mid)
    squeeze_angle = -hi  # degrees each joint closes at the seam stop
    wedge_deg = STOP_SHARE * squeeze_angle

    # Seam plane in the squeezed pose, mapped back onto pod and anchor.
    # The corners line up along the seam there but not in depth, so the plane's
    # normal is the seam tangent turned by the two parts' mean rotation.
    stop = -squeeze_angle
    a_stop = kin.move(anchor_corner, "anchor", stop)
    b_stop = kin.move(pod_corner, "dial-pod", stop)
    seam_point = (a_stop + b_stop) / 2
    turn = 0.5 * (sum(d for _, d in kin.steps("anchor", stop)) + sum(d for _, d in kin.steps("dial-pod", stop)))
    seam_normal = _rot(seam_t, turn)

    def to_design(point: np.ndarray, normal: np.ndarray, part: str) -> tuple[np.ndarray, np.ndarray]:
        for pivot, degrees in reversed(kin.steps(part, stop)):
            point = pivot + _rot(point - pivot, -degrees)
            normal = _rot(normal, -degrees)
        return point, normal

    pod_seam = to_design(seam_point, seam_normal, "dial-pod")
    anchor_seam = to_design(seam_point, seam_normal, "anchor")

    def shape_ends(part: cq.Workplane, name: str) -> cq.Workplane:
        i = CHAIN.index(name)
        if i > 0:
            j = joints[i - 1]
            part = part.cut(_joint_cutter(j["pivot"], j["normal"], j["tangent"], +1, wedge_deg))
        if i < len(CHAIN) - 1:
            j = joints[i]
            part = part.cut(_joint_cutter(j["pivot"], j["normal"], j["tangent"], -1, wedge_deg))
        if name == "dial-pod":
            part = part.cut(_halfspace(pod_seam[0], pod_seam[1], keep_negative=True))
        if name == "anchor":
            part = part.cut(_halfspace(anchor_seam[0], anchor_seam[1], keep_negative=False))
        return part

    # Cord tunnels: anchor knot pocket to pod knot pocket.
    anchor_knot = _arc_angle(profile, ranges["anchor"][1], -ANCHOR_KNOT_FROM_JOINT_MM, JOINT_OFFSET)
    pod_knot = _arc_angle(profile, ranges["dial-pod"][0], POD_KNOT_FROM_END_MM, JOINT_OFFSET)
    cords = None
    for height in CORD_HEIGHTS_MM:
        pts = []
        for angle in np.linspace(anchor_knot, pod_knot, 60):
            p = _ray_hit(profile, JOINT_OFFSET, float(angle))
            pts.append(cq.Vector(float(p[0]), float(p[1]), float(height)))
        tube = _sweep_tube(pts, CORD_TUNNEL_MM)
        cords = tube if cords is None else cords.union(tube)

    pod_inner = SLEEVE_CLEARANCE_MM + POD_STANDOFF_MM
    # The channel keeps the pocket's edge nearest the joint and grows into the body.
    channel_centre = _arc_angle(
        profile, anchor_knot, -(ANCHOR_KNOT_CHANNEL_MM - KNOT_POCKET_MM) / 2, JOINT_OFFSET
    )
    anchor_pockets = _knot_pockets(
        profile, channel_centre, SLEEVE_CLEARANCE_MM, JOINT_OFFSET + 0.6, ANCHOR_KNOT_CHANNEL_MM, joined=True
    )
    pod_pockets = _knot_pockets(profile, pod_knot, pod_inner, JOINT_OFFSET + 0.6)

    # Lace catch on the anchor's outer face, measured from its seam face: a
    # straight slot from the seam face to a round knot pocket.  Both are traps,
    # narrow at the surface and wider underneath, so the lace and knot press
    # in and stay.  The anchor prints upright (v is up), so every roof over a
    # cavity rises at 45 degrees and needs no support.
    seam_face_angle = ranges["anchor"][0]
    u_angle = lambda u: _arc_angle(profile, seam_face_angle, u, JOINT_OFFSET)
    rise = SEGMENT_DOME_WALL_MM + 4.0  # well past the outer surface

    # Knot pocket: a teardrop (round, with a 45 degree point on top) so its
    # roof prints upright without sagging.  The knot bears on the slot's end.
    k, kn, _ = _surface_point(profile, KNOT_FLOOR_OFFSET, u_angle(KNOT_CENTRE_U_MM))
    knot_plane = cq.Plane(
        origin=cq.Vector(float(k[0]), float(k[1]), 0),
        xDir=cq.Vector(0, 0, 1),
        normal=cq.Vector(float(kn[0]), float(kn[1]), 0),
    )
    r = KNOT_POCKET_DIA_MM / 2
    tip = [(r / math.sqrt(2), r / math.sqrt(2)), (r * math.sqrt(2), 0.0), (r / math.sqrt(2), -r / math.sqrt(2))]
    knot_catch = (
        cq.Workplane(knot_plane).circle(r).extrude(rise)
        .union(cq.Workplane(knot_plane).polyline(tip).close().extrude(rise))
    )

    parts: dict[str, cq.Shape] = {}
    band = _ring(profile, SLEEVE_CLEARANCE_MM, SLEEVE_CLEARANCE_MM + SEGMENT_DOME_WALL_MM + 1.0, BAND_HEIGHT_MM)
    for name in CHAIN[:-1]:
        start, end = ranges[name]
        dome = _barrel(profile, start, end, OUTER_EDGE, SLEEVE_CLEARANCE_MM + SEGMENT_DOME_WALL_MM, BAND_HEIGHT_MM, SEGMENT_CROWN_MM)
        raw = band.intersect(_wedge(start - MARGIN_DEG, end + MARGIN_DEG, BAND_HEIGHT_MM)).intersect(dome)
        part = _rounded(shape_ends(raw, name), EDGE_ROUND_MM, name)
        part = part.cut(cords)
        if name == "anchor":
            part = part.cut(anchor_pockets).cut(knot_catch).cut(_lace_slot(profile, part.val(), u_angle))
        label_at = (
            u_angle(LABEL_U_MM[name]) if name in LABEL_U_MM else (start + end) / 2
        )
        part = part.cut(_label(profile, label_at, SLEEVE_CLEARANCE_MM, LABELS[name], LABEL_Z_MM.get(name, 0.0)))
        parts[name] = part.val()

    pod_result = dial_pod.build(
        config,
        prepare=lambda raw: _rounded(shape_ends(raw, "dial-pod"), POD_EDGE_ROUND_MM, "dial-pod"),
        margin_deg=MARGIN_DEG,
    )
    pod_label = _label(profile, pod_knot, pod_inner, LABELS["dial-pod"])  # between its two knot pockets
    parts["dial-pod"] = (
        cq.Workplane().add(pod_result["parts"]["pod"]).cut(cords).cut(pod_pockets).cut(pod_label).val()
    )
    parts["lid"] = pod_result["parts"]["lid"]

    for name, shape in parts.items():
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise RuntimeError(f"{name}: expected one valid solid, got {len(shape.Solids())}")

    return {
        "parts": parts,
        "kinematics": kin,
        "joints": joints,
        "squeeze_angle_deg": squeeze_angle,
        "wedge_deg": wedge_deg,
        "pod": pod_result,
        "ranges": ranges,
        "profile": profile,
    }


def check(result: dict) -> dict:
    parts, kin, joints = result["parts"], result["kinematics"], result["joints"]
    squeeze, wedge = result["squeeze_angle_deg"], result["wedge_deg"]
    pod_body = parts["dial-pod"].fuse(parts["lid"])

    def body(name: str) -> cq.Shape:
        return pod_body if name == "dial-pod" else parts[name]

    def turn(shape: cq.Shape, joint: dict, degrees: float) -> cq.Shape:
        p = joint["pivot"]
        return shape.rotate(cq.Vector(float(p[0]), float(p[1]), 0), cq.Vector(float(p[0]), float(p[1]), 1), degrees)

    # OCC booleans occasionally return an empty intersection for touching
    # faces, so contact is judged by sampling points near the joint line.
    rng = np.random.default_rng(0)

    def shared_points(a: cq.Shape, b: cq.Shape, joint: dict, outer: bool) -> int:
        p, n, t = joint["pivot"], joint["normal"], joint["tangent"]
        hits = 0
        for _ in range(1500):
            depth = rng.uniform(0, 3.5) if outer else -rng.uniform(0, 4.5)
            q = p + t * rng.uniform(-2.0, 2.0) + n * depth
            v = cq.Vector(float(q[0]), float(q[1]), float(rng.uniform(-16, 16)))
            if a.isInside(v) and b.isInside(v):
                hits += 1
        return hits

    report = {"squeeze_angle_per_joint_deg": round(squeeze, 3), "joint_wedge_deg": round(wedge, 3), "joints": []}
    for j in joints:
        left, right = j["between"]
        a, b = body(left), body(right)
        sign = kin.open_sign
        entry = {
            "joint": f"{left} | {right}",
            "shared_points_as_built": shared_points(a, b, j, False),
            "shared_points_at_wedge_close": shared_points(a, turn(b, j, -sign * (wedge - 0.05)), j, False),
            "shared_points_1deg_past_wedge": shared_points(a, turn(b, j, -sign * (wedge + 1.0)), j, False),
            "shared_points_opened_28deg": shared_points(a, turn(b, j, sign * 28.0), j, True),
        }
        if entry["shared_points_as_built"] or entry["shared_points_at_wedge_close"] or entry["shared_points_opened_28deg"]:
            entry["problem"] = "parts collide before they should"
        if not entry["shared_points_1deg_past_wedge"]:
            entry["problem"] = "joint does not stop 1 degree past its wedge"
        report["joints"].append(entry)

    stop = -squeeze
    pod_stop = kin.move_shape(pod_body, "dial-pod", stop)
    anchor_stop = kin.move_shape(parts["anchor"], "anchor", stop)
    report["seam"] = {
        "gap_as_built_mm": round(pod_body.distance(parts["anchor"]), 2),
        "gap_at_squeeze_limit_mm": round(pod_stop.distance(anchor_stop), 3),
        "overlap_at_squeeze_limit_mm3": round(pod_stop.intersect(anchor_stop).Volume(), 3),
    }
    report["walls_mm"] = {
        "segment_skin_over_cord_tunnel_at_ends": round(JOINT_INSET_MM - CORD_TUNNEL_MM / 2, 2),
        "segment_floor_under_cord_tunnel": round(JOINT_OFFSET - CORD_TUNNEL_MM / 2 - SLEEVE_CLEARANCE_MM, 2),
        "pod_floor_under_cord_tunnel": round(JOINT_OFFSET - CORD_TUNNEL_MM / 2 - SLEEVE_CLEARANCE_MM - POD_STANDOFF_MM, 2),
    }
    report["pod_seat"] = result["pod"]["report"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "build" / "brace-parts")
    parser.add_argument("--skip-check", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = build(load_config(args.config))
    for name, shape in result["parts"].items():
        if name == "lid":
            continue
        dial_pod._export(shape, args.output / f"{name}-print-upright.stl")
        cq.exporters.export(shape, str(args.output / f"{name}-print-upright.step"))
        dial_pod._export(_to_local(cq.Workplane().add(shape)), args.output / f"{name}-local.stl")
    dial_pod._export(_to_local(cq.Workplane().add(result["parts"]["lid"])), args.output / "lid-local.stl")
    frame, depth = result["pod"]["frame"], result["pod"]["depth"]
    n = cq.Vector(float(frame.n[0]), float(frame.n[1]), 0)
    axis = n.cross(cq.Vector(0, 0, 1))
    angle = math.degrees(math.acos(max(-1.0, min(1.0, n.dot(cq.Vector(0, 0, 1))))))
    flat = result["parts"]["lid"].rotate(cq.Vector(0, 0, 0), axis, angle)
    bb = flat.BoundingBox()
    flat = flat.translate(cq.Vector(-bb.center.x, -bb.center.y, -bb.zmin))
    dial_pod._export(flat, args.output / "lid-print-flat.stl")
    cq.exporters.export(flat, str(args.output / "lid-print-flat.step"))
    dial_pod._export(
        _to_local(cq.Workplane().add(dial_pod._dial_proxy(frame, depth))), args.output / "dial-proxy-local.stl"
    )
    meta = {
        "joints": [
            {"between": list(j["between"]), "pivot_xy": [round(float(v), 3) for v in j["pivot"]]}
            for j in result["joints"]
        ],
        "open_sign": result["kinematics"].open_sign,
        "squeeze_angle_deg": result["squeeze_angle_deg"],
        "wedge_deg": result["wedge_deg"],
    }
    (args.output / "joints.json").write_text(json.dumps(meta, indent=2) + "\n")
    if not args.skip_check:
        report = check(result)
        (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
