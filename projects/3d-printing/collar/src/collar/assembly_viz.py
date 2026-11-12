"""Export the printable brace assembly for the interactive viewer artifact.

Reads the parts written by `brace_parts.py` (sleeve local frame: x left/right,
y neck axis, z anterior) and writes `build/assembly-viz/assembly.glb` plus
`assembly.json` with the chain order, each joint line, the cord and lace
paths, which part each path point rides on, and the seam gap across the
chain's range from squeezed shut to swung open.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import trimesh

from . import brace_parts as bp
from .config import DEFAULT_CONFIG, PROJECT_ROOT, load_config
from .cord_brace import SLEEVE_CLEARANCE_MM, WALL_MM, _layout, _ray_hit
from .dial_pod import SeatFrame, SEAT_SHIFT_MM
from .sleeve_profile import _reference_outer_profile


CHAIN = bp.CHAIN
FIXED = bp.FIXED_PART
CONTACT_CLOSURE_MM = 5.0  # seam closure that brings the brace onto the sleeve


def _local(xy: np.ndarray, height: float) -> list[float]:
    """Build frame (profile x, profile z, height) to sleeve local (x, y, z)."""
    return [round(float(xy[0]), 2), round(float(-height), 2), round(float(xy[1]), 2)]


def _rotate_y(point: np.ndarray, pivot: np.ndarray, degrees: float) -> np.ndarray:
    """Rotation about +y through `pivot`, as three.js applies it in (x, z)."""
    a = math.radians(degrees)
    x, z = point - pivot
    return pivot + np.array([x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)])


def _chain_move(point: np.ndarray, part: str, pivots: list[np.ndarray], angle: float) -> np.ndarray:
    fixed, index = CHAIN.index(FIXED), CHAIN.index(part)
    if index > fixed:
        for j in range(index - 1, fixed - 1, -1):
            point = _rotate_y(point, pivots[j], angle)
    elif index < fixed:
        for j in range(index, fixed):
            point = _rotate_y(point, pivots[j], -angle)
    return point


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "build" / "assembly-viz")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    config = load_config(args.config)
    profile, *_ = _reference_outer_profile(config)
    ranges = _layout(profile)
    parts_dir = PROJECT_ROOT / "build" / "brace-parts"
    meta = json.loads((parts_dir / "joints.json").read_text())
    pivots = [np.array(j["pivot_xy"]) for j in meta["joints"]]

    outer = SLEEVE_CLEARANCE_MM + WALL_MM
    pod_corner = _ray_hit(profile, outer, ranges["dial-pod"][1])
    anchor_corner = _ray_hit(profile, outer, ranges["anchor"][0])

    def seam_gap(sign: float, angle: float) -> float:
        a = _chain_move(pod_corner, "dial-pod", pivots, sign * angle)
        b = _chain_move(anchor_corner, "anchor", pivots, sign * angle)
        return float(np.linalg.norm(a - b))

    open_sign = 1.0 if seam_gap(1.0, 10.0) > seam_gap(-1.0, 10.0) else -1.0
    squeeze = float(meta["squeeze_angle_deg"])
    samples = sorted({round(-squeeze, 3), -1.0, -0.5, 0.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0})
    design_gap = seam_gap(open_sign, 0.0)
    gap_table = {}
    for a in samples:
        g = seam_gap(open_sign, a)
        gap_table[str(a)] = round(0.0 if a <= -squeeze + 1e-6 else (g if a >= 0 else max(0.0, design_gap * (1 + a / squeeze))), 1)

    def arc_angle(angle: float, arc: float, offset: float) -> float:
        radius = float(np.linalg.norm(_ray_hit(profile, offset, angle)))
        return angle + math.degrees(arc / radius)

    def owner(angle: float) -> str:
        for name in CHAIN:
            a, b = ranges[name]
            for shift in (-360.0, 0.0, 360.0):
                if a - 1.0 <= angle + shift <= b + 1.0:
                    return name
        return min(CHAIN, key=lambda n: min(abs(angle - ranges[n][0]), abs(angle - ranges[n][1])))

    anchor_knot = arc_angle(ranges["anchor"][1], -bp.ANCHOR_KNOT_FROM_JOINT_MM, bp.JOINT_OFFSET)
    pod_knot = arc_angle(ranges["dial-pod"][0], bp.POD_KNOT_FROM_END_MM, bp.JOINT_OFFSET)
    cords = []
    for height in bp.CORD_HEIGHTS_MM:
        cords.append([
            {"p": _local(_ray_hit(profile, bp.JOINT_OFFSET, float(a)), height), "part": owner(float(a))}
            for a in np.linspace(anchor_knot, pod_knot, 120)
        ])

    pod_start, pod_end = ranges["dial-pod"]
    frame = SeatFrame(profile, pod_start, pod_end, SEAT_SHIFT_MM)
    seam_face = ranges["anchor"][0]
    lace = []
    for sign in (1, -1):
        strand = []
        for u, h in ((9.0, 3.0), (13.0, -0.4), (21.0, -0.9)):
            o = frame.origin + frame.t * u + frame.n * h
            strand.append({"p": _local(o, sign * bp.LACE_FACE_V_MM), "part": "dial-pod"})
        p = _ray_hit(profile, outer - 1.6, pod_end - 0.5)
        strand.append({"p": _local(p, sign * bp.LACE_FACE_V_MM), "part": "dial-pod"})
        lace_depth = bp.OUTER_EDGE - 1.5
        for u, v in ((0.0, 0.8), (6.0, 0.6), (bp.KNOT_CENTRE_U_MM - 2.0, 0.4)):
            p = _ray_hit(profile, lace_depth, arc_angle(seam_face, u, bp.JOINT_OFFSET))
            strand.append({"p": _local(p, sign * v), "part": "anchor"})
        lace.append(strand)

    scene = trimesh.Scene()
    sources = {
        "sleeve": PROJECT_ROOT / "build" / "cord-brace" / "sleeve-local.stl",
        **{name: parts_dir / f"{name}-local.stl" for name in CHAIN},
        "lid": parts_dir / "lid-local.stl",
        "dial": parts_dir / "dial-proxy-local.stl",
    }
    for name, path in sources.items():
        mesh = trimesh.load_mesh(path, process=True)
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    scene.export(args.output / "assembly.glb", include_normals=True)

    (args.output / "assembly.json").write_text(
        json.dumps(
            {
                "chain": CHAIN,
                "fixed": FIXED,
                "joints": [{"between": j["between"], "pivot_xz": j["pivot_xy"]} for j in meta["joints"]],
                "open_sign": open_sign,
                "squeeze_angle_deg": round(squeeze, 3),
                "seam_gap_at_deg": gap_table,
                "contact_closure_mm": CONTACT_CLOSURE_MM,
                "design_seam_gap_mm": round(design_gap, 1),
                "cords": cords,
                "lace": lace,
                "pod_normal": [round(float(frame.n[0]), 4), 0.0, round(float(frame.n[1]), 4)],
                "lace_payout_mm": 254.0,
            }
        )
    )
    print(f"wrote {args.output}: open_sign {open_sign}, seam gap table {gap_table}")


if __name__ == "__main__":
    main()
