"""sheet_corners.py <upload.json> <sheet_long_mm> <sheet_short_mm>

For a sheet of known non-standard size (the torn-out notebook page, 282.75 x 211.05 mm
measured through the dot grid), map Tracefinity's detected corners to a virtual A4
rectangle centred on the sheet, so `paper_size: a4` gives the right scale on both axes.
Assumes detected corners are TL, TR, BR, BL with the long side on top (landscape).
"""
import json
import sys

import cv2
import numpy as np

u = json.load(open(sys.argv[1]))
L, S = float(sys.argv[2]), float(sys.argv[3])
px = np.array([[p["x"], p["y"]] for p in u["detected_corners"]], np.float32)
top = np.linalg.norm(px[1] - px[0])
side = np.linalg.norm(px[3] - px[0])
W, Hh = (L, S) if top >= side else (S, L)
AW, AH = (297.0, 210.0) if top >= side else (210.0, 297.0)
sheet = np.array([[0, 0], [W, 0], [W, Hh], [0, Hh]], np.float32)
H = cv2.getPerspectiveTransform(sheet, px)
ox, oy = (W - AW) / 2, (Hh - AH) / 2
rect = np.array([[ox, oy], [ox + AW, oy], [ox + AW, oy + AH], [ox, oy + AH]], np.float32)
c = cv2.perspectiveTransform(rect[None], H)[0]
print(json.dumps({"corners": [{"x": round(float(x), 1), "y": round(float(y), 1)} for x, y in c]}))
