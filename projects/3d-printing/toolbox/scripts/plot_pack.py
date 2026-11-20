"""plot_pack.py <pack.json> <out.png> [inset]

Top view of a packing: bin outline, usable rectangle, each tool outline and its
pocket top (tool grown by clearance + chamfer, 2 mm), labelled, in bin-space mm
(y down, matching Tracefinity)."""
import json
import sys
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely import affinity
from shapely.geometry import Polygon

pk = json.load(open(sys.argv[1]))
inset = float(sys.argv[3]) if len(sys.argv) > 3 else 4.85
W, H = pk["nx"] * 42, pk["ny"] * 42
fig, ax = plt.subplots(figsize=(W / 18, H / 18), dpi=110)
ax.add_patch(plt.Rectangle((0.25, 0.25), W - 0.5, H - 0.5, fill=False, lw=1.5, ec="#333"))
ax.add_patch(plt.Rectangle((inset, inset), W - 2 * inset, H - 2 * inset, fill=False, lw=0.8, ls="--", ec="#999"))
colors = ["#c0392b", "#2471a3", "#1e8449", "#b9770e"]
for t, c in zip(pk["tools"], colors):
    tool = json.loads(urllib.request.urlopen(f"http://localhost:3900/api/tools/{t['id']}").read())
    p = Polygon([(q["x"], q["y"]) for q in tool["points"]]).buffer(0)
    minx, miny, maxx, maxy = p.bounds
    p = affinity.translate(p, -(minx + maxx) / 2, -(miny + maxy) / 2)
    if t["mirror"]:
        p = affinity.scale(p, 1, -1, origin=(0, 0))
    p = affinity.rotate(p, t["rotation"], origin=(0, 0))
    minx, miny, maxx, maxy = p.bounds
    p = affinity.translate(p, t["cx"] - (minx + maxx) / 2, t["cy"] - (miny + maxy) / 2)
    pocket = p.buffer(2.0)
    ax.fill(*pocket.exterior.xy, color=c, alpha=0.15)
    ax.plot(*p.exterior.xy, color=c, lw=1.2)
    label = t["name"].split(" (")[0] + (" (flipped)" if t["mirror"] else "")
    ax.text(p.centroid.x, p.centroid.y, label, ha="center", va="center", fontsize=8, color=c, weight="bold")
ax.set_xlim(-2, W + 2)
ax.set_ylim(H + 2, -2)
ax.set_aspect("equal")
ax.set_title(f"{pk['nx']}x{pk['ny']} bin ({W:.0f} x {H:.0f} mm), tightest tool-to-tool gap {pk['min_gap']} mm", fontsize=9)
ax.tick_params(labelsize=7)
plt.tight_layout()
plt.savefig(sys.argv[2])
