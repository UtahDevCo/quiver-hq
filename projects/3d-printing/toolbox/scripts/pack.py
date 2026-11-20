"""pack.py <spec.json> <tools.json> <out.json>

Nest tool outlines into the smallest Gridfinity bin. Raster bottom-left fill:
every tool is rasterised at RES mm for each orientation (STEP-degree rotations,
plus a mirror flip where allowed); FFT correlation against the forbidden mask
(placed tools grown by `sep`, plus everything outside the usable rectangle) gives
every collision-free position at once. Tools go in one at a time at the lowest,
then leftmost free spot, trying every placement order and every orientation per
tool, and keeping the layout whose used height is smallest. The winner is
re-checked exactly with shapely (gaps and containment) before it is written.
Runs inside the tracefinity container (numpy, scipy, cv2, shapely).

spec:  {"sep", "inset", "sizes": [[nx, ny], ...], "step": deg, "res": mm,
        "tools": [{"id", "mirror_ok"}]}
tools: {id: {"name", "points": [[x, y], ...]}}  (fetched by the caller)
out:   {"nx", "ny", "min_gap", "min_edge", "tools": [{"id", "name", "mirror", "rotation", "cx", "cy"}]}
       rotation in degrees (Tracefinity's convention, y down), applied after the
       mirror; cx, cy = bounding-box centre in bin mm.
"""
import itertools
import json
import sys

import cv2
import numpy as np
from scipy.signal import fftconvolve
from shapely import affinity
from shapely.geometry import Polygon, box

spec = json.load(open(sys.argv[1]))
tools = json.load(open(sys.argv[2]))
SEP, INSET = spec["sep"], spec["inset"]
STEP, RES = spec.get("step", 5), spec.get("res", 0.5)
GRID = 42.0

base = []
for t in spec["tools"]:
    p = Polygon(tools[t["id"]]["points"]).buffer(0)
    minx, miny, maxx, maxy = p.bounds
    base.append({"id": t["id"], "name": tools[t["id"]]["name"],
                 "poly": affinity.translate(p, -(minx + maxx) / 2, -(miny + maxy) / 2),
                 "mirror_ok": t.get("mirror_ok", False)})


def oriented(p, mirror, rot):
    if mirror:
        p = affinity.scale(p, 1, -1, origin=(0, 0))
    p = affinity.rotate(p, rot, origin=(0, 0))
    minx, miny, maxx, maxy = p.bounds
    return affinity.translate(p, -minx, -miny)  # top-left of bbox at origin


def raster(p, grow=0.0):
    q = p.buffer(grow, 16) if grow else p
    minx, miny, maxx, maxy = q.bounds
    h, w = int(np.ceil((maxy - miny) / RES)) + 2, int(np.ceil((maxx - minx) / RES)) + 2
    m = np.zeros((h, w), np.uint8)
    for ring in [q.exterior]:
        pts = np.round((np.array(ring.coords) - [minx, miny]) / RES).astype(np.int32)
        cv2.fillPoly(m, [pts], 1)
    return m, (minx, miny)


orients = []
for b in base:
    opts = []
    for mirror in ([False, True] if b["mirror_ok"] else [False]):
        for rot in np.arange(0, 360, STEP):
            p = oriented(b["poly"], mirror, float(rot))
            m, _ = raster(p)
            opts.append({"mirror": mirror, "rot": float(rot), "poly": p, "mask": m.astype(np.float32)})
    orients.append(opts)


def place_all(order, W, H):
    """greedy bottom-left; returns (used_height, placements) or None"""
    gw, gh = int(round(W / RES)), int(round(H / RES))
    placed = []
    forbid = np.zeros((gh, gw), np.float32)
    x0 = y0 = INSET
    ux, uy = int(round(x0 / RES)), int(round(y0 / RES))
    uw, uh = int(round((W - 2 * INSET) / RES)), int(round((H - 2 * INSET) / RES))
    forbid[:] = 1
    forbid[uy:uy + uh, ux:ux + uw] = 0
    for i in order:
        best = None
        for o in orients[i]:
            m = o["mask"]
            if m.shape[0] > gh or m.shape[1] > gw:
                continue
            hit = fftconvolve(forbid, m[::-1, ::-1], mode="valid")
            free = np.argwhere(hit < 0.5)
            if not len(free):
                continue
            # lowest bottom edge first, then leftmost
            bottoms = free[:, 0] + m.shape[0]
            k = np.lexsort((free[:, 1], bottoms))[0]
            cand = (bottoms[k], free[k, 1], free[k, 0], o)
            if best is None or cand[:2] < best[:2]:
                best = cand
        if best is None:
            return None
        _, cx, cy, o = best
        poly = affinity.translate(o["poly"], cx * RES, cy * RES)
        placed.append((i, o, poly))
        g, (gx, gy) = raster(poly, SEP)
        gx, gy = int(round(gx / RES)), int(round(gy / RES))
        ys, xs = slice(max(gy, 0), min(gy + g.shape[0], gh)), slice(max(gx, 0), min(gx + g.shape[1], gw))
        forbid[ys, xs] = np.maximum(forbid[ys, xs], g[ys.start - gy:ys.stop - gy, xs.start - gx:xs.stop - gx])
    used = max(p.bounds[3] for _, _, p in placed)
    return used, placed


def exact_ok(placed, W, H):
    region = box(INSET, INSET, W - INSET, H - INSET)
    polys = [p for _, _, p in placed]
    gaps = [polys[a].distance(polys[b]) for a in range(len(polys)) for b in range(a + 1, len(polys))]
    edge = min(region.exterior.distance(p) if region.contains(p) else -1 for p in polys)
    return min(gaps), edge


for nx, ny in spec["sizes"]:
    for W, H in ((nx * GRID, ny * GRID), (ny * GRID, nx * GRID)):
        best = None
        for order in itertools.permutations(range(len(base))):
            r = place_all(order, W, H)
            if r and (best is None or r[0] < best[0]):
                best = r
        if not best:
            print(f"{W:.0f} x {H:.0f}: no fit", flush=True)
            continue
        used, placed = best
        gap, edge = exact_ok(placed, W, H)
        print(f"{W:.0f} x {H:.0f}: fits, used height {used:.1f}, min gap {gap:.2f}, min edge {edge:.2f}", flush=True)
        if gap < SEP - RES or edge < 0:
            print("  exact check failed, skipping")
            continue
        out = {"nx": round(W / GRID), "ny": round(H / GRID), "min_gap": round(gap, 2), "min_edge": round(edge, 2), "tools": []}
        for i, o, p in sorted(placed, key=lambda r: r[0]):
            minx, miny, maxx, maxy = p.bounds
            out["tools"].append({"id": base[i]["id"], "name": base[i]["name"], "mirror": o["mirror"],
                                 "rotation": o["rot"], "cx": round((minx + maxx) / 2, 2), "cy": round((miny + maxy) / 2, 2)})
        json.dump(out, open(sys.argv[3], "w"), indent=1)
        print(json.dumps(out, indent=1))
        sys.exit(0)
print("no feasible size")
sys.exit(1)
