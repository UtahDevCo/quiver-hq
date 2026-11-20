import sys, glob, cv2, numpy as np
src, out, crop = sys.argv[1], sys.argv[2], sys.argv[3] == "crop"
tiles = []
for f in sorted(glob.glob(src + "/*.jpg")):
    im = cv2.imread(f)
    if crop:  # crop around drawn outlines (pure red/blue/green strokes)
        b, g, r = cv2.split(im)
        m = ((r > 200) & (g < 60) & (b < 60)) | ((b > 200) & (g < 60) & (r < 60)) | ((g > 140) & (r < 40) & (b < 40))
        ys, xs = np.nonzero(m)
        if len(xs):
            x0, x1, y0, y1 = max(0, xs.min() - 80), xs.max() + 80, max(0, ys.min() - 80), ys.max() + 80
            im = im[y0:y1, x0:x1]
    h, w = im.shape[:2]
    s = 700 / max(h, w)
    im = cv2.resize(im, (int(w * s), int(h * s)))
    t = np.full((720, 720, 3), 255, np.uint8)
    t[:im.shape[0], :im.shape[1]] = im
    cv2.putText(t, f.split("/")[-1][13:22], (5, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    tiles.append(t)
while len(tiles) % 4: tiles.append(np.full((720, 720, 3), 255, np.uint8))
rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
cv2.imwrite(out, np.vstack(rows))
