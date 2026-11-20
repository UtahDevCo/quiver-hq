"""layout.py <bin_id> <grid_x> <grid_y> <spec.json>

spec: [{"tool_id":..., "rotation": deg, "cx": mm, "cy": mm, "depth": mm|null}, ...]  (cx, cy = bounding-box centre)
Places tools the same way bin_service.sync_placed_tools does (library points
rotated about their centroid, moved to the placed centroid), so a later GET
does not move anything. Prints each tool's bbox in bin mm.
"""
import json
import math
import sys
import urllib.request

API = "http://localhost:3900/api"
bin_id, gx, gy, spec_path = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
spec = json.load(open(spec_path))


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b"null")


b = call("GET", f"/bins/{bin_id}")
by_tool = {pt["tool_id"]: pt for pt in b["placed_tools"]}


def place(pts, lcx, lcy, rot, cx, cy):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [{"x": cx + (p["x"] - lcx) * c - (p["y"] - lcy) * s, "y": cy + (p["x"] - lcx) * s + (p["y"] - lcy) * c} for p in pts]


for item in spec:
    tool = call("GET", f"/tools/{item['tool_id']}")
    lp = tool["points"]
    lcx, lcy = sum(p["x"] for p in lp) / len(lp), sum(p["y"] for p in lp) / len(lp)
    pt = by_tool[item["tool_id"]]
    # cx/cy name the bounding-box centre; convert to the centroid the sync rule uses
    probe = place(lp, lcx, lcy, item["rotation"], 0.0, 0.0)
    bx = (min(p["x"] for p in probe) + max(p["x"] for p in probe)) / 2
    by = (min(p["y"] for p in probe) + max(p["y"] for p in probe)) / 2
    args = (lcx, lcy, item["rotation"], item["cx"] - bx, item["cy"] - by)
    pt["rotation"] = item["rotation"]
    pt["points"] = place(lp, *args)
    pt["interior_rings"] = [place(r, *args) for r in tool.get("interior_rings") or []]
    for fh, src in zip(pt["finger_holes"], tool.get("finger_holes") or []):
        q = place([src], *args)[0]
        fh["x"], fh["y"] = q["x"], q["y"]
    pt["depth_override"] = item.get("depth")
    xs, ys = [p["x"] for p in pt["points"]], [p["y"] for p in pt["points"]]
    print(f"{pt['name']}: x {min(xs):.1f}..{max(xs):.1f}  y {min(ys):.1f}..{max(ys):.1f}  depth {pt['depth_override']}")

b["bin_config"]["grid_x"], b["bin_config"]["grid_y"] = gx, gy
call("PUT", f"/bins/{bin_id}", {k: b[k] for k in ("name", "bin_config", "placed_tools")})
print(f"bin {gx}x{gy} = {gx*42:.0f} x {gy*42:.0f} mm")
