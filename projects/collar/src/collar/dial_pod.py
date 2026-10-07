"""Printable dial pod: the brace's rear pod with the dial base captured for good.

The dial never leaves the pod.  Popping the dial lets the lace pay out, which
opens the seam for putting the collar on or taking it off, so the base only
has to be held, not slid in and out (a top-opening slot would collide with the
sleeve's upper flare).

The flat dial base sits in a flat seat cut along a plane just inside the pod's
curved face.  The seat is the proven v4-v7 fit: an oval pocket 39.97 x 37.67 mm
(round flange plus the ear), 1.0 mm deep.  Above the plane:
- the trailing half (away from the seam) is a separate lid, screwed down with
  two M3 screws into heat-set inserts; its top is the pod's own curved face;
- the seam half is the pod itself, which laps over the flange; windows above
  and below its centre block let each lace drop below the flange rim and run
  out toward the seam.

Assembly: tuck the base's seam edge under the pod's lip (tilt the trailing
side up a few degrees and slide toward the seam), lay it flat, thread the
laces out through the windows, then screw the lid on.

Print the pod upright (as exported, neck axis vertical): the laps become
ordinary walls and the seat's ceiling is a 1 mm bridge.  Print the lid flat on
its underside.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

from .config import DEFAULT_CONFIG, PROJECT_ROOT, load_config
from .cord_brace import (
    POD_STANDOFF_MM,
    POD_WALL_MM,
    SLEEVE_CLEARANCE_MM,
    _layout,
    _ray_hit,
    _to_local,
    pod_build_frame,
)
from .sleeve_profile import _reference_outer_profile


BASE_DIAMETER_MM = 37.37
BASE_ACROSS_EAR_MM = 39.65
HOUSING_CLEAR_RADIUS_MM = 14.835  # 28.27 mm across the lace bosses, plus 0.7 mm
SEAT_WIDTH_MM = 37.67  # 0.3 mm over the flange
EAR_EXTRA_MM = BASE_ACROSS_EAR_MM - BASE_DIAMETER_MM
SEAT_DEPTH_MM = 1.0  # 0.94 mm flange; the proven v4/v5 gap
MIN_COVER_MM = 1.6  # thinnest lid allowed over the flange
MIN_LAP_MM = 1.2  # thinnest seam-side lap: a short, stiff edge of the pod itself

LID_SEAM_EDGE_U_MM = 4.0  # the lid covers u below this; the pod laps above it
LID_TRAILING_EDGE_U_MM = -26.0
WINDOW_INNER_V_MM = 8.0  # lace windows span |v| from here...
WINDOW_OUTER_V_MM = 16.0  # ...to here; the strands leave the dial near |v| = 12
# Lid tongues: the lid's top and bottom strips run past its front edge into
# slots under the pod's lip, so the lid is held at the front as well as by the
# two screws at the back.  Hook the front in first, lay it flat, then screw.
TONGUE_V_MM = (16.5, 20.0)
TONGUE_LENGTH_MM = 3.5
TONGUE_THICKNESS_MM = 1.2
TONGUE_CLEARANCE_MM = 0.25
WINDOW_DROP_MM = 0.6  # windows reach this far below the seat floor
WINDOW_END_U_MM = 40.0

SCREW_POINTS_UV = ((-19.0, 16.5), (-19.0, -16.5))
# The seat sits this far toward the seam from the pod's middle, which leaves
# the trailing end clear for the cord knot pockets and shortens the lace run.
SEAT_SHIFT_MM = 6.0
SCREW_CLEARANCE_MM = 3.4
INSERT_HOLE_MM = 4.6  # kit's figure for its 5 mm OD x 4 mm M3 inserts (min depth 4.1, wall 2)
INSERT_DEPTH_MM = 5.5


def _checked(shape: cq.Workplane, step: str) -> cq.Workplane:
    """Fail at the operation that breaks the solid, not three steps later."""
    solid = shape.val()
    if not solid.isValid():
        raise RuntimeError(f"pod geometry became invalid at: {step}")
    return shape


class SeatFrame:
    """Tangent frame at the pod's mid point: u toward the seam, v up, n outward."""

    def __init__(self, profile, start: float, end: float, shift_mm: float = 0.0) -> None:
        offset = SLEEVE_CLEARANCE_MM + POD_STANDOFF_MM + POD_WALL_MM
        mid = (start + end) / 2
        mean_radius = float(np.linalg.norm(_ray_hit(profile, offset, mid)))
        mid += math.degrees(shift_mm / mean_radius)
        self.origin = _ray_hit(profile, offset, mid)
        a, b = _ray_hit(profile, offset, mid - 0.5), _ray_hit(profile, offset, mid + 0.5)
        t = (b - a) / np.linalg.norm(b - a)  # CCW, which is toward the seam
        n = np.array([t[1], -t[0]])
        self.t = t
        self.n = n if n @ self.origin > 0 else -n

    def point(self, u: float, v: float, h: float, depth: float) -> cq.Vector:
        """Point at height h above the seat plane (plane is `depth` below the face)."""
        p = self.origin + self.t * u + self.n * (h - depth)
        return cq.Vector(float(p[0]), float(p[1]), float(v))

    def plane(self, depth: float, h: float = 0.0) -> cq.Plane:
        return cq.Plane(
            origin=self.point(0.0, 0.0, h, depth),
            xDir=cq.Vector(float(self.t[0]), float(self.t[1]), 0),
            normal=cq.Vector(float(self.n[0]), float(self.n[1]), 0),
        )


def _face_drop(pod: cq.Shape, frame: SeatFrame, u: float, v: float) -> float:
    """How far the pod's outer face lies below the tangent plane at (u, v)."""
    lo, hi = 0.0, 20.0
    inside = lambda k: pod.isInside(frame.point(u, v, -k, 0.0))
    if inside(0.0):
        return 0.0
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if inside(mid) else (mid, hi)
    return hi


def _prism(frame: SeatFrame, depth: float, h0: float, h1: float, sketch) -> cq.Workplane:
    """Extrude a sketch drawn on the seat plane from height h0 to h1."""
    wp = cq.Workplane(frame.plane(depth, h0))
    return sketch(wp, h1 - h0)


def build(config: dict, prepare=None, margin_deg: float = 0.0) -> dict:
    """Build the pod and lid.  `prepare` may reshape the raw pod (end faces,
    fillets) before the seat, lid, windows and inserts are cut into it."""
    profile, *_ = _reference_outer_profile(config)
    start, end = _layout(profile)["dial-pod"]
    pod = pod_build_frame(profile, start, end, margin_deg, round_edges=prepare is None)
    if prepare is not None:
        pod = prepare(pod)
    pod_shape = pod.val()
    frame = SeatFrame(profile, start, end, SEAT_SHIFT_MM)

    r = SEAT_WIDTH_MM / 2
    ring = [(r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
    lid_points = [(u, v) for u, v in ring if u <= LID_SEAM_EDGE_U_MM] + [(-SEAT_WIDTH_MM / 2 - EAR_EXTRA_MM, 0.0)]
    lap_points = [(u, v) for u, v in ring if u > LID_SEAM_EDGE_U_MM and abs(v) < WINDOW_INNER_V_MM]
    drops = {p: _face_drop(pod_shape, frame, *p) for p in lid_points + lap_points + list(SCREW_POINTS_UV)}
    depth = max(
        max(drops[p] for p in lid_points + list(SCREW_POINTS_UV)) + MIN_COVER_MM,
        max(drops[p] for p in lap_points) + MIN_LAP_MM,
    )
    lap_cover = min(depth - drops[p] for p in lap_points)

    def seat(wp, h):
        """Round flange seat stretched toward the trailing side for the ear."""
        return (
            wp.circle(SEAT_WIDTH_MM / 2).extrude(h)
            .union(wp.center(-EAR_EXTRA_MM, 0).circle(SEAT_WIDTH_MM / 2).extrude(h))
            .union(wp.center(-EAR_EXTRA_MM / 2, 0).rect(EAR_EXTRA_MM, SEAT_WIDTH_MM).extrude(h))
        )

    def lid_region(wp, h):
        u0, u1 = LID_TRAILING_EDGE_U_MM, LID_SEAM_EDGE_U_MM
        return wp.center((u0 + u1) / 2, 0).rect(u1 - u0, 80).extrude(h)

    def opening(wp, h):
        return wp.circle(HOUSING_CLEAR_RADIUS_MM).extrude(h)

    def windows(wp, h):
        edge = WINDOW_OUTER_V_MM
        u0, u1 = LID_SEAM_EDGE_U_MM, WINDOW_END_U_MM
        a = wp.center((u0 + u1) / 2, (WINDOW_INNER_V_MM + edge) / 2).rect(u1 - u0, edge - WINDOW_INNER_V_MM).extrude(h)
        b = wp.center((u0 + u1) / 2, -(WINDOW_INNER_V_MM + edge) / 2).rect(u1 - u0, edge - WINDOW_INNER_V_MM).extrude(h)
        return a.union(b)

    def holes(diameter):
        def sketch(wp, h):
            return wp.pushPoints(list(SCREW_POINTS_UV)).circle(diameter / 2).extrude(h)
        return sketch

    above = 25.0
    lid_cut = _prism(frame, depth, 0.0, above, lid_region)
    _checked(pod, "prepared pod")
    def tongues(clearance):
        def sketch(wp, h):
            u0 = LID_SEAM_EDGE_U_MM - 1.0
            u1 = LID_SEAM_EDGE_U_MM + TONGUE_LENGTH_MM + clearance
            v0, v1 = TONGUE_V_MM[0] - clearance, TONGUE_V_MM[1] + clearance
            a = wp.center((u0 + u1) / 2, (v0 + v1) / 2).rect(u1 - u0, v1 - v0).extrude(h)
            b = wp.center((u0 + u1) / 2, -(v0 + v1) / 2).rect(u1 - u0, v1 - v0).extrude(h)
            return a.union(b)
        return sketch

    tongue_solid = pod.intersect(_prism(frame, depth, 0.0, TONGUE_THICKNESS_MM, tongues(0.0)))
    tongue_slot = _prism(frame, depth, -0.01, TONGUE_THICKNESS_MM + TONGUE_CLEARANCE_MM, tongues(TONGUE_CLEARANCE_MM))
    lid = _checked(pod.intersect(lid_cut).union(tongue_solid), "lid region with tongues")
    lid = _checked(lid.cut(_prism(frame, depth, -0.5, above, opening)), "lid opening")
    lid = _checked(lid.cut(_prism(frame, depth, -0.5, above, holes(SCREW_CLEARANCE_MM))), "lid screw holes")

    base = _checked(pod.cut(lid_cut).cut(tongue_slot), "pod minus lid and tongue slots")
    base = _checked(base.cut(_prism(frame, depth, -SEAT_DEPTH_MM, 0.0, seat)), "seat")
    base = _checked(base.cut(_prism(frame, depth, 0.0, above, opening)), "housing opening")
    base = _checked(base.cut(_prism(frame, depth, -SEAT_DEPTH_MM - WINDOW_DROP_MM, above, windows)), "lace windows")
    base = _checked(base.cut(_prism(frame, depth, -INSERT_DEPTH_MM, 0.5, holes(INSERT_HOLE_MM))), "insert holes")

    parts = {"pod": base.val(), "lid": lid.val()}
    for name, shape in parts.items():
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise RuntimeError(f"{name} should be one valid solid, got {len(shape.Solids())}")

    floor = min(
        _inner_depth(profile, frame, u) - depth - SEAT_DEPTH_MM - WINDOW_DROP_MM
        for u in (-EAR_EXTRA_MM, 0.0, 10.0, SEAT_WIDTH_MM / 2)
    )
    insert_wall = min(
        _inner_depth(profile, frame, u) - depth - INSERT_DEPTH_MM for u, _ in SCREW_POINTS_UV
    )
    report = {
        "seat_plane_depth_below_face_mm": round(depth, 2),
        "thinnest_lid_over_flange_mm": round(min(depth - drops[p] for p in lid_points), 2),
        "thinnest_lap_over_flange_mm": round(lap_cover, 2),
        "lid_thickness_at_screws_mm": [round(depth - drops[p], 2) for p in SCREW_POINTS_UV],
        "thinnest_floor_under_seat_mm": round(floor, 2),
        "material_behind_inserts_mm": round(insert_wall, 2),
    }
    return {"parts": parts, "frame": frame, "depth": depth, "report": report}


def _inner_depth(profile, frame: SeatFrame, u: float) -> float:
    """Distance from the tangent plane at the face down to the pod's inner surface."""
    from shapely.geometry import LineString

    inner = profile.buffer(SLEEVE_CLEARANCE_MM + POD_STANDOFF_MM)
    p = frame.origin + frame.t * u
    hit = inner.exterior.intersection(LineString([tuple(p), tuple(p - frame.n * 40)]))
    points = [hit] if hit.geom_type == "Point" else list(hit.geoms)
    return min(float(np.linalg.norm(np.array(q.coords[0]) - p)) for q in points)


def _dial_proxy(frame: SeatFrame, depth: float) -> cq.Shape:
    floor = frame.point(0.0, 0.0, -SEAT_DEPTH_MM, depth)
    n = cq.Vector(float(frame.n[0]), float(frame.n[1]), 0)
    flange = cq.Solid.makeCylinder(BASE_DIAMETER_MM / 2, 0.94, floor, n)
    housing = cq.Solid.makeCylinder(26.84 / 2, 18.0, floor + n * 0.94, n)
    return flange.fuse(housing)


def _export(shape: cq.Shape, path: Path) -> None:
    """Export, then close the few seam triangles OCC leaves where the pod's
    elliptic taper meets its end faces (the B-rep itself is valid)."""
    cq.exporters.export(shape, str(path), tolerance=0.05, angularTolerance=0.1)
    mesh = trimesh.load(path, process=True)
    if not mesh.is_watertight:
        volume = mesh.volume
        mesh.merge_vertices()
        mesh.update_faces(mesh.nondegenerate_faces())
        mesh.update_faces(mesh.unique_faces())
        trimesh.repair.fill_holes(mesh)
        trimesh.repair.fix_normals(mesh)
        if mesh.is_watertight and abs(mesh.volume - volume) <= 0.5:
            mesh.export(path)
            return
        edges = np.sort(mesh.edges, axis=1)
        _, counts = np.unique(edges, axis=0, return_counts=True)
        print(
            f"warning: {path.name} keeps {int((counts != 2).sum())} bad mesh edges; "
            f"import the matching .step into the slicer instead"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "build" / "dial-pod")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = build(load_config(args.config))
    pod, lid, frame = result["parts"]["pod"], result["parts"]["lid"], result["frame"]

    _export(pod, args.output / "dial-pod-print-upright.stl")
    # Lid underside (the seat plane) down: rotate its outward normal onto +Z.
    n = cq.Vector(float(frame.n[0]), float(frame.n[1]), 0)
    axis = n.cross(cq.Vector(0, 0, 1))
    angle = math.degrees(math.acos(max(-1.0, min(1.0, n.dot(cq.Vector(0, 0, 1))))))
    lid_flat = lid.rotate(cq.Vector(0, 0, 0), axis, angle)
    bb = lid_flat.BoundingBox()
    lid_flat = lid_flat.translate(cq.Vector(-bb.center.x, -bb.center.y, -bb.zmin))
    _export(lid_flat, args.output / "dial-pod-lid-print-flat.stl")

    for name, shape in (("pod", pod), ("lid", lid), ("dial-proxy", _dial_proxy(frame, result["depth"]))):
        _export(_to_local(cq.Workplane("XY").add(shape)), args.output / f"{name}-local.stl")
    (args.output / "report.json").write_text(json.dumps(result["report"], indent=2) + "\n")
    print(json.dumps(result["report"], indent=2))


if __name__ == "__main__":
    main()
