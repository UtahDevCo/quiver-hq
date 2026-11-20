"""slide.py <bin.json> <tool.json> <name> <out.json> [sep] [inset] [W] [H]

Slide one placed tool as far left (-x) as it will go, allowing a small vertical
shift and rotation, while keeping `sep` mm from every other tool except the
odds-and-ends box (which is regrown afterwards) and `inset` mm from the bin edge.
Geometry follows Tracefinity's placement rule: library points rotated about their
centroid. Prints and writes the new {rotation, cx, cy} (cx, cy = bbox centre).
Runs inside the tracefinity container (shapely).
"""
import json
import sys

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

b = json.load(open(sys.argv[1]))
lib = json.load(open(sys.argv[2]))
name, out = sys.argv[3], sys.argv[4]
SEP = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0
INSET = float(sys.argv[6]) if len(sys.argv) > 6 else 4.85
W = float(sys.argv[7]) if len(sys.argv) > 7 else 210.0
H = float(sys.argv[8]) if len(sys.argv) > 8 else 84.0

me = next(t for t in b["placed_tools"] if t["name"] == name)
others = unary_union([Polygon([(p["x"], p["y"]) for p in t["points"]]).buffer(0)
                      for t in b["placed_tools"] if t["name"] not in (name, "odds and ends box")])
region = box(INSET, INSET, W - INSET, H - INSET)
lp = Polygon([(p["x"], p["y"]) for p in lib["points"]]).buffer(0)
lc = lp.centroid


def at(rot, cx, cy):
    p = affinity.rotate(lp, rot, origin=lc)  # Tracefinity: x cos - y sin, y-down data
    minx, miny, maxx, maxy = p.bounds
    return affinity.translate(p, cx - (minx + maxx) / 2, cy - (miny + maxy) / 2)


def ok(p):
    return region.contains(p) and p.distance(others) >= SEP


cur = Polygon([(p["x"], p["y"]) for p in me["points"]])
minx, miny, maxx, maxy = cur.bounds
cx0, cy0, rot0 = (minx + maxx) / 2, (miny + maxy) / 2, me["rotation"]
assert ok(at(rot0, cx0, cy0)), "current placement already violates the constraints"
best = (cx0, rot0, cy0)
for dr in np.arange(-4, 4.01, 0.5):
    for dy in np.arange(-6, 6.01, 0.5):
        lo, hi = cx0 - 120, cx0
        if not ok(at(rot0 + dr, hi, cy0 + dy)):
            continue
        for _ in range(30):  # bisect the leftmost feasible x on this line (feasible set is an interval near hi)
            mid = (lo + hi) / 2
            if ok(at(rot0 + dr, mid, cy0 + dy)):
                hi = mid
            else:
                lo = mid
        # bisection can jump a gap; walk back right until the path from cx0 is clear
        x = hi
        while any(not ok(at(rot0 + dr, xx, cy0 + dy)) for xx in np.arange(x, cx0, 1.0)):
            x += 0.5
        p = at(rot0 + dr, x, cy0 + dy)
        left = p.bounds[0]
        if left < at(best[1], best[0], best[2]).bounds[0] - 1e-6:
            best = (x, rot0 + dr, cy0 + dy)
cx, rot, cy = best
p = at(rot, cx, cy)
print(f"{name}: moved {cx0 - cx:.1f} mm left, {cy - cy0:+.1f} mm down, rotation {rot0:.1f} -> {rot:.1f}; "
      f"gap to others {p.distance(others):.2f} mm; bbox x {p.bounds[0]:.1f}..{p.bounds[2]:.1f}")
json.dump({"rotation": round(rot, 2), "cx": round(cx, 2), "cy": round(cy, 2)}, open(out, "w"))
