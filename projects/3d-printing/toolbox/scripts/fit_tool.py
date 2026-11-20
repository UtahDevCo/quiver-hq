"""fit_tool.py <tool_id> <length_mm> [<width_mm>] [--name NAME]

Scale a library tool's outline to caliper measurements. Even at 60 cm the traces
ran 2 to 3.5% long, from parallax on the tool's raised top surface. The outline is
scaled along its minimum-area bounding box: the long axis to `length`, the short
axis to `width` (or by the same factor as the length when no width is given).
Interior rings and finger holes get the same transform. Bins pick up the change on
their next GET (sync_placed_tools).
"""
import argparse
import json
import math
import urllib.request

import numpy as np

API = "http://localhost:3900/api"


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b"null")


def min_area_frame(pts):
    """angle (rad) of the long axis of the minimum-area bounding rectangle, plus its extents"""
    best = None
    for deg in np.arange(0, 180, 0.1):
        a = math.radians(deg)
        u = np.array([math.cos(a), math.sin(a)])
        v = np.array([-u[1], u[0]])
        pu, pv = pts @ u, pts @ v
        L, W = np.ptp(pu), np.ptp(pv)
        if best is None or L * W < best[0]:
            best = (L * W, a, L, W)
    _, a, L, W = best
    if W > L:
        a, L, W = a + math.pi / 2, W, L
    return a, L, W


ap = argparse.ArgumentParser()
ap.add_argument("tool_id")
ap.add_argument("length", type=float)
ap.add_argument("width", type=float, nargs="?")
ap.add_argument("--name")
args = ap.parse_args()

tool = call("GET", f"/tools/{args.tool_id}")
P = np.array([[p["x"], p["y"]] for p in tool["points"]])
c = P.mean(0)
a, L, W = min_area_frame(P - c)
su = args.length / L
sv = (args.width / W) if args.width else su
u = np.array([math.cos(a), math.sin(a)])
v = np.array([-u[1], u[0]])
M = np.outer(u, u) * su + np.outer(v, v) * sv  # scale along u and v


def tf(arr):
    return (np.asarray(arr) - c) @ M.T + c


def pts(arr):
    return [{"x": round(float(x), 3), "y": round(float(y), 3)} for x, y in tf(arr)]


body = {"points": pts(P)}
if tool.get("interior_rings"):
    body["interior_rings"] = [pts([[q["x"], q["y"]] for q in r]) for r in tool["interior_rings"]]
if tool.get("finger_holes"):
    fh = []
    for h in tool["finger_holes"]:
        x, y = tf([[h["x"], h["y"]]])[0]
        fh.append({**h, "x": float(x), "y": float(y)})
    body["finger_holes"] = fh
if args.name:
    body["name"] = args.name
call("PUT", f"/tools/{args.tool_id}", body)

a2, L2, W2 = min_area_frame(tf(P) - c)
print(f"{args.name or tool['name']}: traced {L:.1f} x {W:.1f} -> {L2:.2f} x {W2:.2f} mm (x{su:.4f} along, x{sv:.4f} across)")
