"""widen_band.py <tool.json> <from_mm> <to_mm> <width_mm> <out.json>

Union a straight band of `width_mm` into a tool outline, running along the
outline's long axis from `from_mm` to `to_mm` (measured from the end with the
wider extreme, i.e. the head). The band is centred on the outline's own
centreline. Use it where the tracer eroded a dark, round handle below its caliper
diameter. Rasterises at 0.05 mm and traces the union back to a polygon. Runs
inside the tracefinity container (cv2, numpy). Writes {"points": [...]} for
PUT /api/tools/{id}.
"""
import json
import sys

import cv2
import numpy as np

src, a_mm, b_mm, width, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
t = json.load(open(src))
P = np.array([[p["x"], p["y"]] for p in t["points"]], np.float32)
(cx, cy), (w, h), ang = cv2.minAreaRect(P)
a = np.radians(ang if w >= h else ang + 90)
u = np.array([np.cos(a), np.sin(a)])
v = np.array([-u[1], u[0]])
c = np.array([cx, cy])
pu, pv = (P - c) @ u, (P - c) @ v

res = 20.0  # px per mm
pad = width
ox, oy = pu.min() - pad, pv.min() - pad
Q = np.column_stack([pu - ox, pv - oy]) * res
m = np.zeros((int(Q[:, 1].max() + pad * res) + 2, int(Q[:, 0].max() + pad * res) + 2), np.uint8)
cv2.fillPoly(m, [np.round(Q).astype(np.int32)], 255)

# head end = the end whose 10% slice is wider
L = pu.max() - pu.min()
def slice_width(lo, hi):
    sel = (pu >= lo) & (pu <= hi)
    return np.ptp(pv[sel]) if sel.sum() > 2 else 0
head_at_min = slice_width(pu.min(), pu.min() + 0.1 * L) >= slice_width(pu.max() - 0.1 * L, pu.max())
def along(mm):
    return pu.min() + mm if head_at_min else pu.max() - mm

# centreline from the middle of the outline at the two band ends
def centre(at):
    col = m[:, int(round((at - ox) * res))]
    ys = np.nonzero(col)[0]
    return (ys.min() + ys.max()) / 2 / res + oy
x0, x1 = sorted([along(a_mm), along(b_mm)])
y0, y1 = centre(x0 + 1.0), centre(x1 - 1.0)
band = np.array([[x0, y0 - width / 2], [x1, y1 - width / 2], [x1, y1 + width / 2], [x0, y0 + width / 2]])
B = (band - [ox, oy]) * res
cv2.fillPoly(m, [np.round(B).astype(np.int32)], 255)

cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cnt = max(cs, key=cv2.contourArea)
cnt = cv2.approxPolyDP(cnt, 0.03 * res, True).reshape(-1, 2).astype(np.float64)
loc = cnt / res + [ox, oy]
world = c + np.outer(loc[:, 0], u) + np.outer(loc[:, 1], v)
json.dump({"points": [{"x": round(float(x), 3), "y": round(float(y), 3)} for x, y in world]}, open(out, "w"))
print(f"band {a_mm}-{b_mm} mm x {width} mm; {len(P)} -> {len(world)} points")
