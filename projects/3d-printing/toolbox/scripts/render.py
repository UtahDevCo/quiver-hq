"""render.py <out.png> <stl> [<stl> ...] : shaded isometric renders side by side"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

out, paths = sys.argv[1], sys.argv[2:]
fig = plt.figure(figsize=(7 * len(paths), 6), dpi=110)
light = np.array([0.4, -0.5, 0.8])
light /= np.linalg.norm(light)
for i, p in enumerate(paths):
    m = trimesh.load(p, force="mesh")
    ax = fig.add_subplot(1, len(paths), i + 1, projection="3d")
    shade = np.clip(m.face_normals @ light, 0, 1) * 0.65 + 0.3
    cols = np.column_stack([shade * 0.35, shade * 0.6, shade * 0.95, np.ones_like(shade)])
    pc = Poly3DCollection(m.triangles, facecolors=cols, edgecolor="none")
    ax.add_collection3d(pc)
    lo, hi = m.bounds
    span = (hi - lo).max()
    c = (hi + lo) / 2
    ax.set_xlim(c[0] - span / 2, c[0] + span / 2)
    ax.set_ylim(c[1] - span / 2, c[1] + span / 2)
    ax.set_zlim(c[2] - span / 2, c[2] + span / 2)
    ax.view_init(elev=48, azim=-62)
    ax.set_axis_off()
    ax.set_title(p.split("/")[-1].replace(".stl", "") + f"  {hi[0]-lo[0]:.0f}x{hi[1]-lo[1]:.0f}x{hi[2]-lo[2]:.0f} mm")
plt.tight_layout()
plt.savefig(out)
