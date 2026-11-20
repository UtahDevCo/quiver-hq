"""overlay.py <corrected.jpg> <trace.json> <scale_mm_per_px> <out.jpg>

Draws traced polygons on the corrected image and estimates the dot-grid pitch
(px) from blank paper via autocorrelation, so scale can be checked against the
notebook's printed grid instead of the assumed paper size.
"""
import json
import sys

import cv2
import numpy as np

img_path, trace_path, scale, out_path = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
img = cv2.imread(img_path)
trace = json.load(open(trace_path))
h, w = img.shape[:2]

mask = np.zeros((h, w), np.uint8)
colors = [(0, 0, 255), (255, 0, 0), (0, 160, 0), (200, 0, 200), (0, 140, 255)]
for i, poly in enumerate(trace["polygons"]):
    pts = np.array([[p["x"], p["y"]] for p in poly["points"]], np.int32)
    cv2.fillPoly(mask, [pts], 255)
    c = colors[i % len(colors)]
    cv2.polylines(img, [pts], True, c, 3)
    x0, y0 = pts.min(0)
    x1, y1 = pts.max(0)
    rect = cv2.minAreaRect(pts.astype(np.float32))
    L, W = sorted(rect[1], reverse=True)
    txt = f"{poly['label']}: {L*scale:.1f} x {W*scale:.1f} mm"
    cv2.putText(img, txt, (int(x0), max(30, int(y0) - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, c, 2)
    print(txt)


def pitch(gray):
    """dominant dot spacing in px along x and y from blank paper"""
    g = gray.astype(np.float32)
    g = g - cv2.GaussianBlur(g, (0, 0), 8)
    g = -g  # dots are dark
    g[g < 0] = 0
    out = []
    for axis in (1, 0):
        prof = g.sum(axis=1 - axis) if axis == 1 else g.sum(axis=1)
        prof = prof - prof.mean()
        ac = np.correlate(prof, prof, "full")[len(prof) - 1:]
        lo = 8
        k = lo + int(np.argmax(ac[lo:120]))
        # refine to sub-pixel with a parabola
        a, b, c = ac[k - 1], ac[k], ac[k + 1]
        out.append(k + 0.5 * (a - c) / (a - 2 * b + c))
    return out


gray = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2GRAY)
blank = cv2.dilate(mask, np.ones((61, 61), np.uint8))
# central patch of paper away from tools and edges
patch_candidates = []
ph = pw = 400
for y in range(int(h * 0.1), int(h * 0.9) - ph, 100):
    for x in range(int(w * 0.1), int(w * 0.85) - pw, 100):
        if blank[y:y + ph, x:x + pw].max() == 0:
            patch_candidates.append((x, y))
if patch_candidates:
    x, y = patch_candidates[len(patch_candidates) // 2]
    px, py = pitch(gray[y:y + ph, x:x + pw])
    cv2.rectangle(img, (x, y), (x + pw, y + ph), (0, 200, 200), 2)
    print(f"dot_pitch_px x={px:.2f} y={py:.2f} -> at scale {scale:.4f}: {px*scale:.3f} x {py*scale:.3f} mm")
    print(f"if grid is 5mm: true scale x={5/px:.4f} y={5/py:.4f} (ratio to assumed {5/px/scale:.3f}, {5/py/scale:.3f})")
print(f"corrected_size_px={w}x{h} -> {w*scale:.1f} x {h*scale:.1f} mm")
cv2.imwrite(out_path, img)
