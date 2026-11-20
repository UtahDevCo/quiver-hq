"""grid_corners.py <upload.jpg> <pitch_mm> <debug_out.jpg>

Calibrate from the notebook's dot grid instead of the paper outline.
Detects dots, grows integer lattice indices by BFS, fits a homography
lattice-mm -> image px, then projects a virtual A4 rectangle (centred on the
detected grid, long side along the grid's longer extent) into the image.
Prints JSON: {corners, n_dots, rms_px, grid_extent_dots, page_hint}.
"""
import json
import sys
from collections import deque

import cv2
import numpy as np

path, pitch_mm, dbg_path = sys.argv[1], float(sys.argv[2]), sys.argv[3]
img = cv2.imread(path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# small dark spots on light paper
bh = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
_, th = cv2.threshold(bh, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
n, lab, stats, cent = cv2.connectedComponentsWithStats(th)
keep = []
for k in range(1, n):
    x, y, w, h, a = stats[k]
    if 2 <= a <= 40 and w <= 8 and h <= 8 and 0.4 < w / max(h, 1) < 2.5:
        # require bright surround: paper, not marble vein or tool texture
        y0, y1, x0, x1 = max(0, y - 6), y + h + 6, max(0, x - 6), x + w + 6
        ring = gray[y0:y1, x0:x1]
        if np.percentile(ring, 70) > 150:
            keep.append(cent[k])
pts = np.array(keep, np.float32)

# basis vectors from nearest-neighbour displacements
from numpy.linalg import norm
d = pts[:, None, :] - pts[None, :, :] if len(pts) < 6000 else None
if d is None:
    sys.exit("too many blobs")
dist = norm(d, axis=2)
np.fill_diagonal(dist, 1e9)
nn = np.argsort(dist, axis=1)[:, :4]
vecs = np.concatenate([pts[nn[:, k]] - pts for k in range(4)])
lens = norm(vecs, axis=1)
step = np.median(norm(pts[nn[:, 0]] - pts, axis=1))
vecs = vecs[(lens > 0.7 * step) & (lens < 1.3 * step)]
ang = np.mod(np.arctan2(vecs[:, 1], vecs[:, 0]), np.pi)  # fold to [0, pi)
hist, edges = np.histogram(ang, bins=180, range=(0, np.pi))
a1 = edges[np.argmax(hist)] + np.pi / 360
mask2 = np.abs(np.angle(np.exp(1j * (ang - a1)))) > np.pi / 4
a2 = np.median(ang[mask2])
b1 = np.array([np.cos(a1), np.sin(a1)]) * step
b2 = np.array([np.cos(a2), np.sin(a2)]) * step
# make b1 the more horizontal one, both pointing +x / +y
if abs(b1[0]) < abs(b2[0]):
    b1, b2 = b2, b1
if b1[0] < 0:
    b1 = -b1
if b2[1] < 0:
    b2 = -b2

# BFS lattice growth with locally refined basis, from several seeds; keep the largest
tree_r = 0.3 * step


def grow(seed):
    idx = {seed: (0, 0)}
    local = {seed: (b1.copy(), b2.copy())}
    taken = {(0, 0): seed}
    q = deque([seed])
    while q:
        s = q.popleft()
        i, j = idx[s]
        lb1, lb2 = local[s]
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
            key = (i + di, j + dj)
            if key in taken:
                continue
            pred = pts[s] + di * lb1 + dj * lb2
            dd = norm(pts - pred, axis=1)
            c = int(np.argmin(dd))
            if dd[c] < tree_r and c not in idx:
                idx[c] = key
                taken[key] = c
                nb1, nb2 = lb1.copy(), lb2.copy()
                v = (pts[c] - pts[s])
                if di:
                    nb1 = 0.5 * nb1 + 0.5 * v / di
                else:
                    nb2 = 0.5 * nb2 + 0.5 * v / dj
                local[c] = (nb1, nb2)
                q.append(c)
    return idx


rng = np.random.default_rng(0)
best = {}
order = np.argsort(norm(pts - np.median(pts, axis=0), axis=1))
for seed in list(order[:40]) + list(rng.choice(len(pts), min(80, len(pts)), replace=False)):
    r = grow(int(seed))
    if len(r) > len(best):
        best = r
idx = best

# global refinement: fit H, predict all lattice nodes, snap, refit
for _ in range(4):
    ids = np.array(list(idx.keys()))
    grid = np.array([idx[k] for k in ids], np.float32) * pitch_mm
    H, inl = cv2.findHomography(grid, pts[ids], cv2.RANSAC, 2.0)
    gi0 = np.array([idx[k] for k in ids])
    ri = range(gi0[:, 0].min() - 60, gi0[:, 0].max() + 61)
    rj = range(gi0[:, 1].min() - 60, gi0[:, 1].max() + 61)
    nodes = np.array([(i, j) for i in ri for j in rj], np.float32)
    pred = cv2.perspectiveTransform(nodes[None] * pitch_mm, H)[0]
    # nearest blob per prediction (local step size from H)
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    dd, nearest = tree.query(pred)
    ok = dd < 0.25 * step
    idx = {}
    used = set()
    for (i, j), c, good in zip(nodes.astype(int), nearest, ok):
        if good and c not in used:
            idx[c] = (int(i), int(j))
            used.add(c)

ids = np.array(list(idx.keys()))
grid = np.array([idx[k] for k in ids], np.float32) * pitch_mm
img_pts = pts[ids]
H, inl = cv2.findHomography(grid, img_pts, cv2.RANSAC, 1.5)
inl = inl.ravel().astype(bool)
proj = cv2.perspectiveTransform(grid[inl][None], H)[0]
rms = float(np.sqrt(np.mean(np.sum((proj - img_pts[inl]) ** 2, axis=1))))

gi = np.array([idx[k] for k in ids])[inl]
ext_i = int(gi[:, 0].max() - gi[:, 0].min()) + 1
ext_j = int(gi[:, 1].max() - gi[:, 1].min()) + 1
cx = float(np.median(gi[:, 0])) * pitch_mm
cy = float(np.median(gi[:, 1])) * pitch_mm
W, Hh = (297.0, 210.0) if ext_i >= ext_j else (210.0, 297.0)
rect = np.array([[cx - W / 2, cy - Hh / 2], [cx + W / 2, cy - Hh / 2], [cx + W / 2, cy + Hh / 2], [cx - W / 2, cy + Hh / 2]], np.float32)
corners = cv2.perspectiveTransform(rect[None], H)[0]

# order TL, TR, BR, BL in image space
s_ = corners.sum(1)
df = corners[:, 1] - corners[:, 0]
ordered = [corners[np.argmin(s_)], corners[np.argmin(df)], corners[np.argmax(s_)], corners[np.argmax(df)]]

dbg = img.copy()
for p in img_pts[inl]:
    cv2.circle(dbg, (int(p[0]), int(p[1])), 3, (0, 200, 0), -1)
for p in img_pts[~inl]:
    cv2.circle(dbg, (int(p[0]), int(p[1])), 4, (0, 0, 255), -1)
cv2.polylines(dbg, [np.array(ordered, np.int32)], True, (255, 0, 255), 3)
cv2.imwrite(dbg_path, dbg)

# sheet outline: convex hull of inlier dots that sit in dense lattice neighbourhoods
from scipy.spatial import cKDTree as _KD
ip = img_pts[inl]
cnt = np.array([len(v) for v in _KD(ip).query_ball_point(ip, 1.6 * step)])
dense = ip[cnt >= 5]
hull = cv2.convexHull(dense.astype(np.float32)).reshape(-1, 2) if len(dense) >= 3 else np.zeros((0, 2))

print(json.dumps({
    "hull": [[round(float(x), 1), round(float(y), 1)] for x, y in hull],
    "corners": [{"x": round(float(p[0]), 1), "y": round(float(p[1]), 1)} for p in ordered],
    "n_blobs": len(pts), "n_dots": int(inl.sum()), "rms_px": round(rms, 2),
    "step_px": round(float(step), 2),
    "H": [[float(v) for v in row] for row in H],
    "grid_extent_dots": [ext_i, ext_j],
    "grid_extent_mm": [round((ext_i - 1) * pitch_mm, 1), round((ext_j - 1) * pitch_mm, 1)],
}))
