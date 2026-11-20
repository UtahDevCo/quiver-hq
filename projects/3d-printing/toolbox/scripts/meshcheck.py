import sys, trimesh, numpy as np
m = trimesh.load(sys.argv[1], force="mesh")
lo, hi = m.bounds
print(f"watertight={m.is_watertight} size={hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f} mm vol={m.volume/1000:.1f} cm3")
# pocket floors: upward faces below the rim, grouped by height
up = m.face_normals[:, 2] > 0.99
z = m.triangles_center[up, 2]
area = m.area_faces[up]
top = hi[2]
for h in sorted(set(np.round(z, 1))):
    a = area[np.round(z, 1) == h].sum()
    if a > 50:
        print(f"  flat face z={h:.1f} (depth below top {top-h:.1f}) area={a:.0f} mm2")
