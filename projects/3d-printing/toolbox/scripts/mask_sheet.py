"""mask_sheet.py <photo> <frame_w> <polygon.json> <grow_px> <out.jpg>

Replace everything outside the sheet with the paper's own shading so the saliency tracer can only
find the tools on the page. polygon.json holds [[x, y], ...] in the 2048-px
upload frame (frame_w is that frame's width); grow_px (upload-frame px, may be
negative) dilates or shrinks it. Writes a full-resolution JPEG with orientation
baked in.
"""
import json
import sys

import cv2
import numpy as np

photo, frame_w, poly_path, grow, out = sys.argv[1], float(sys.argv[2]), sys.argv[3], float(sys.argv[4]), sys.argv[5]
img = cv2.imread(photo)  # applies EXIF orientation, matching Tracefinity's ingest
k = img.shape[1] / frame_w
poly = (np.array(json.load(open(poly_path)), np.float32) * k).astype(np.int32)
mask = np.zeros(img.shape[:2], np.uint8)
cv2.fillPoly(mask, [poly], 255)
r = int(abs(grow) * k)
if r:
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    mask = cv2.dilate(mask, ker) if grow > 0 else cv2.erode(mask, ker)
# continue the paper's own shading outward instead of a flat fill, so no edge
# is left for the saliency model: inpaint at low resolution, then upsample
h, w = mask.shape
f = 8
small = cv2.resize(img, (w // f, h // f), interpolation=cv2.INTER_AREA)
smask = cv2.resize(mask, (w // f, h // f), interpolation=cv2.INTER_NEAREST)
smask = cv2.erode(smask, np.ones((5, 5), np.uint8))  # drop the sheet's darker edge band
fill = cv2.inpaint(small, 255 - smask, 9, cv2.INPAINT_TELEA)
fill = cv2.GaussianBlur(fill, (0, 0), 3)
fill = cv2.resize(fill, (w, h), interpolation=cv2.INTER_CUBIC)
alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 3 * k)[..., None]
img = (img * alpha + fill * (1 - alpha)).astype(np.uint8)
cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
print(out, img.shape)
