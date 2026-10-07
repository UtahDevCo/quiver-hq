"""Cord-strung brace concept around the fitted sleeve (look study).

Four domed segments, a long dial pod at the back that swells to 42 mm at the dial
and tapers to band height at its ends, and a lace-anchor piece sit on the
sleeve's smooth 38 mm waist.  The seam sits beside the pod, over the sleeve's
rear opening.  In the intended build two low-stretch cords run
through every part just inside the outer surface, so the chain opens by
pivoting about its outer edge without changing cord length, and the inner end
faces meet at the designed ring shape as the minimum-circumference stop.  The
BOA closes the single seam between the dial pod and the anchor piece.

This module renders the look only: no cord tunnels, slot cartridge, or lace
anchor yet.  Geometry is built in the sleeve's local frame (profile in x/z,
neck axis along y, anterior +z), the same frame `outer_brace.py` uses.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

from .config import DEFAULT_CONFIG, PROJECT_ROOT, load_config
from .full_sleeve import _build_full_sleeve_shapes
from .outer_brace import _reference_outer_profile


SLEEVE_CLEARANCE_MM = 0.8
WALL_MM = 8.0  # segment thickness at its ends
SEGMENT_DOME_WALL_MM = 10.0  # segment thickness at its middle
SEGMENT_CROWN_MM = 1.5  # vertical drop of the dome at top and bottom edges
BAND_HEIGHT_MM = 36.0
EDGE_ROUND_MM = 2.5
SEGMENT_GAP_MM = 1.5
# Seam gap with the brace wrapped loosely (0.8 mm off the sleeve).  Closing it
# takes about 5 mm to reach the sleeve plus 8 mm of squeeze, after which the
# pod's and anchor's seam faces meet: the hard minimum-circumference stop.
SEAM_GAP_MM = 13.0

SEGMENT_COUNT = 5
POD_CENTER_ANGLE_DEG = -90.0  # posterior, over the sleeve's rear opening; anterior is +90
DIAL_POD_ARC_MM = 62.0  # just clockwise of the seam; short enough to wrap the back
ANCHOR_ARC_MM = 40.0  # just counter-clockwise of the seam

# The 37.4 mm dial base is taller than the 36 mm band.  The pod is the
# smallest that holds the 37.67 mm pocket with 2 mm walls above and below,
# reaching 3 mm onto each flare, where it stands off them slightly.  Its face
# is no thicker than a segment's.
POD_HEIGHT_MM = 43.0  # 42 plus 1 so the 37.67 mm seat keeps 2 mm walls at its sides
POD_STANDOFF_MM = 1.2
# 1.5 mm prouder than a segment at the dial, so the flat seat cut into the
# curved face keeps a real floor; the dome still falls to segment thickness at
# the pod ends.
POD_EXTRA_THICKNESS_MM = 1.5
POD_WALL_MM = SEGMENT_DOME_WALL_MM - POD_STANDOFF_MM + POD_EXTRA_THICKNESS_MM
POD_CROWN_MM = 0.5  # nearly flat vertically, so the flat seat stays inside the face
POD_EDGE_ROUND_MM = 3.0
DIAL_BASE_DIAMETER_MM = 37.37
DIAL_HOUSING_DIAMETER_MM = 28.27
DIAL_HEIGHT_MM = 18.0


def _spline_face(polygon: Polygon, samples: int = 160) -> cq.Workplane:
    ring = np.asarray(polygon.exterior.coords)[:-1]
    angles = np.unwrap(np.arctan2(ring[:, 1], ring[:, 0]))
    order = np.argsort(angles)
    ring, angles = ring[order], angles[order]
    targets = np.linspace(angles[0], angles[0] + 2 * math.pi, samples, endpoint=False)
    xs = np.interp(targets, angles, ring[:, 0], period=2 * math.pi)
    zs = np.interp(targets, angles, ring[:, 1], period=2 * math.pi)
    points = [cq.Vector(float(x), float(z), 0) for x, z in zip(xs, zs)]
    edge = cq.Edge.makeSpline(points, periodic=True)
    return cq.Workplane("XY").add(cq.Wire.assembleEdges([edge]))


def _ring(profile: Polygon, inner_offset: float, outer_offset: float, height: float) -> cq.Workplane:
    outer = _spline_face(profile.buffer(outer_offset)).toPending().extrude(height)
    inner = _spline_face(profile.buffer(inner_offset)).toPending().extrude(height)
    return outer.cut(inner).translate((0, 0, -height / 2))


def _wedge(start_deg: float, end_deg: float, height: float) -> cq.Workplane:
    far = 400.0
    steps = max(2, int(abs(end_deg - start_deg) // 4) + 1)
    points = [(0.0, 0.0)] + [
        (
            far * math.cos(math.radians(start_deg + (end_deg - start_deg) * i / steps)),
            far * math.sin(math.radians(start_deg + (end_deg - start_deg) * i / steps)),
        )
        for i in range(steps + 1)
    ]
    return (
        cq.Workplane("XY")
        .polyline(points)
        .close()
        .extrude(height + 2)
        .translate((0, 0, -height / 2 - 1))
    )


def _arc_table(profile: Polygon) -> tuple[np.ndarray, np.ndarray]:
    """Absolute polar angle (degrees, increasing) against cumulative mid-wall arc length."""
    mid = profile.buffer(SLEEVE_CLEARANCE_MM + WALL_MM / 2)
    coords = np.asarray(mid.exterior.coords)
    angles = np.degrees(np.unwrap(np.arctan2(coords[:, 1], coords[:, 0])))
    if angles[-1] < angles[0]:
        coords, angles = coords[::-1], angles[::-1]
    lengths = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(coords, axis=0).T))])
    return angles, lengths


def _layout(profile: Polygon) -> dict[str, tuple[float, float]]:
    """Angular ranges (degrees, CCW) for every part.

    Parts run counter-clockwise from the seam: anchor, segments, dial pod.  The
    seam is placed so the dial pod is centred on POD_CENTER_ANGLE_DEG, and all
    spacing is by arc length along the mid-wall, so non-circular sections still
    get equal segments.
    """
    angles, lengths = _arc_table(profile)
    total = lengths[-1]

    def arc_at(angle_deg: float) -> float:
        wrapped = angles[0] + (angle_deg - angles[0]) % 360.0
        return float(np.interp(wrapped, angles, lengths))

    def angle_at(arc: float) -> float:
        return float(np.interp(arc % total, lengths, angles))

    segment_arc = (
        total
        - SEAM_GAP_MM
        - DIAL_POD_ARC_MM
        - ANCHOR_ARC_MM
        - (SEGMENT_COUNT + 1) * SEGMENT_GAP_MM
    ) / SEGMENT_COUNT
    seam = arc_at(POD_CENTER_ANGLE_DEG) + SEAM_GAP_MM / 2 + DIAL_POD_ARC_MM / 2
    ranges: dict[str, tuple[float, float]] = {}
    cursor = SEAM_GAP_MM / 2
    pieces = [("anchor", ANCHOR_ARC_MM)] + [
        (f"segment-{i + 1}", segment_arc) for i in range(SEGMENT_COUNT)
    ] + [("dial-pod", DIAL_POD_ARC_MM)]
    for name, arc in pieces:
        first, last = angle_at(seam + cursor), angle_at(seam + cursor + arc)
        if last < first:
            last += 360.0
        ranges[name] = (first, last)
        cursor += arc + SEGMENT_GAP_MM
    return ranges


def _to_local(shape: cq.Workplane) -> cq.Shape:
    """Build frame (profile in XY, height on Z) to sleeve local (x, y=axis, z)."""
    return shape.val().rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)


def _rounded(part: cq.Workplane, radius: float, name: str) -> cq.Workplane:
    """Round every edge, stepping the radius down if OCC refuses; report it."""
    for attempt in (radius, radius * 0.75, radius * 0.5, radius * 0.35):
        try:
            rounded = part.edges().fillet(attempt)
        except Exception:
            continue
        if not rounded.val().isValid():
            continue  # OCC sometimes returns a fillet that is not a valid solid
        if attempt != radius:
            print(f"note: {name} rounded at {attempt:.2f} mm instead of {radius} mm")
        return rounded
    print(f"warning: could not round {name} at any radius down to {radius * 0.35:.2f} mm; left sharp")
    return part


def _ray_hit(profile: Polygon, offset: float, angle_deg: float) -> np.ndarray:
    """Point where a ray from the profile centre crosses the offset surface."""
    surface = profile.buffer(offset)
    ray = np.array([math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))])
    reach = max(np.hypot(*np.asarray(surface.exterior.coords).T)) + 5
    hit = surface.exterior.intersection(LineString([(0, 0), tuple(ray * reach)]))
    point = hit if hit.geom_type == "Point" else list(hit.geoms)[0]
    return np.array(point.coords[0])


def _circle_through(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> tuple[np.ndarray, float]:
    ax, ay = a
    bx, by = b
    cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    centre = np.array([ux, uy])
    return centre, float(np.linalg.norm(a - centre))


def _barrel(
    profile: Polygon,
    start_deg: float,
    end_deg: float,
    edge_offset: float,
    centre_offset: float,
    height: float,
    crown: float,
) -> cq.Workplane:
    """Solid whose outer face domes along the arc and crowns vertically.

    Its vertical axis and radius come from a circle through the part's two end
    points at edge_offset and its midpoint at centre_offset, so the dome
    follows the real sleeve profile.  The vertical crown drops by `crown` at
    the top and bottom edges.
    """
    mid = (start_deg + end_deg) / 2
    centre, radius = _circle_through(
        _ray_hit(profile, edge_offset, start_deg),
        _ray_hit(profile, centre_offset, mid),
        _ray_hit(profile, edge_offset, end_deg),
    )
    half = height / 2 + 1.0
    rho = ((height / 2) ** 2 + crown**2) / (2 * crown)
    zs = np.linspace(-half, half, 41)
    rs = radius - rho + np.sqrt(np.maximum(rho**2 - zs**2, 0.0))
    outline = [(0.0, -half)] + [(float(r), float(z)) for r, z in zip(rs, zs)] + [(0.0, half)]
    solid = (
        cq.Workplane("XZ")
        .polyline(outline)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    return solid.translate((float(centre[0]), float(centre[1]), 0))


def _pod_taper(profile: Polygon, start_deg: float, end_deg: float) -> cq.Workplane:
    """Elliptic prism along the pod's mid ray: 50 mm tall at the dial, 36 at the ends."""
    mid = (start_deg + end_deg) / 2
    point = _ray_hit(profile, SLEEVE_CLEARANCE_MM + WALL_MM / 2, mid)
    radial = np.array([math.cos(math.radians(mid)), math.sin(math.radians(mid))])
    tangent = np.array([-radial[1], radial[0]])
    semi_height = POD_HEIGHT_MM / 2
    edge_ratio = (BAND_HEIGHT_MM / 2) / semi_height
    semi_arc = (DIAL_POD_ARC_MM / 2) / math.sqrt(1 - edge_ratio**2)
    plane = cq.Plane(
        origin=cq.Vector(float(point[0]), float(point[1]), 0),
        xDir=cq.Vector(float(tangent[0]), float(tangent[1]), 0),
        normal=cq.Vector(float(radial[0]), float(radial[1]), 0),
    )
    return cq.Workplane(plane).ellipse(semi_arc, semi_height).extrude(60, both=True)


def pod_build_frame(
    profile: Polygon, start: float, end: float, margin_deg: float = 0.0, round_edges: bool = True
) -> cq.Workplane:
    """The dial pod in the build frame (profile in XY, neck axis on Z).

    `margin_deg` extends the pod past its layout ends so printable joint faces
    can be cut back to the joint lines.
    """
    inner = SLEEVE_CLEARANCE_MM + POD_STANDOFF_MM
    centre = inner + POD_WALL_MM
    # Oversize the ring and dome so the elliptic taper alone forms the top and
    # bottom; a tangent contact there defeats the fillet.
    tall = POD_HEIGHT_MM + 6.0
    ring = _ring(profile, inner, centre + 1.0, tall)
    dome = _barrel(profile, start, end, SLEEVE_CLEARANCE_MM + WALL_MM, centre, tall, POD_CROWN_MM)
    wedge = _wedge(start - margin_deg, end + margin_deg, tall)
    piece = ring.intersect(wedge).intersect(dome).intersect(_pod_taper(profile, start, end))
    return _rounded(piece, POD_EDGE_ROUND_MM, "dial-pod") if round_edges else piece


def build_parts(config: dict) -> dict[str, cq.Shape]:
    profile, *_ = _reference_outer_profile(config)
    ranges = _layout(profile)
    inner = SLEEVE_CLEARANCE_MM
    segment_edge = inner + WALL_MM
    segment_centre = inner + SEGMENT_DOME_WALL_MM
    band = _ring(profile, inner, segment_centre + 1.0, BAND_HEIGHT_MM)
    parts: dict[str, cq.Shape] = {}
    for name, (start, end) in ranges.items():
        wedge = _wedge(start, end, POD_HEIGHT_MM + 6.0)
        if name == "dial-pod":
            piece = pod_build_frame(profile, start, end)
        else:
            dome = _barrel(profile, start, end, segment_edge, segment_centre, BAND_HEIGHT_MM, SEGMENT_CROWN_MM)
            piece = _rounded(band.intersect(wedge).intersect(dome), EDGE_ROUND_MM, name)
        parts[name] = _to_local(piece)

    start, end = ranges["dial-pod"]
    mid = (start + end) / 2
    hit = _ray_hit(profile, inner + POD_STANDOFF_MM + POD_WALL_MM, mid)
    ray = np.array([math.cos(math.radians(mid)), math.sin(math.radians(mid))])
    origin = cq.Vector(float(hit[0]), float(hit[1]), 0)
    normal = cq.Vector(float(ray[0]), float(ray[1]), 0)
    base = cq.Solid.makeCylinder(DIAL_BASE_DIAMETER_MM / 2, 1.0, origin, normal)
    housing = cq.Solid.makeCylinder(
        DIAL_HOUSING_DIAMETER_MM / 2, DIAL_HEIGHT_MM, origin + normal * 1.0, normal
    )
    parts["dial"] = _to_local(cq.Workplane("XY").add(base.fuse(housing)))
    return parts


def _mesh(shape: cq.Shape, path: Path) -> trimesh.Trimesh:
    cq.exporters.export(shape, str(path), tolerance=0.08, angularTolerance=0.12)
    return trimesh.load_mesh(path, process=False)


def _render(output: Path, items: list[tuple[trimesh.Trimesh, tuple[float, float, float], float]]) -> None:
    import vtk

    from .fit_scene import _vtk_actor

    bounds = np.vstack([mesh.bounds for mesh, _, _ in items])
    center = (bounds.min(axis=0) + bounds.max(axis=0)) / 2
    views = [
        ("Front", (0.0, 0.15, 1.0)),
        ("Side", (1.0, 0.15, 0.2)),
        ("Back (dial)", (0.0, 0.15, -1.0)),
        ("Rear three-quarter", (0.8, 0.45, -0.8)),
    ]
    window = vtk.vtkRenderWindow()
    window.SetSize(2400, 700)
    window.SetOffScreenRendering(1)
    for index, (title, direction) in enumerate(views):
        renderer = vtk.vtkRenderer()
        renderer.SetViewport(index / 4, 0, (index + 1) / 4, 1)
        renderer.SetBackground(0.96, 0.965, 0.97)
        for mesh, color, opacity in items:
            renderer.AddActor(_vtk_actor(mesh, color, opacity))
        d = np.asarray(direction) / np.linalg.norm(direction)
        camera = renderer.GetActiveCamera()
        camera.SetFocalPoint(*center)
        camera.SetPosition(*(center + d * 900))
        camera.SetViewUp(0, 1, 0)
        camera.ParallelProjectionOn()
        renderer.ResetCamera()
        camera.Zoom(1.15)
        label = vtk.vtkTextActor()
        label.SetInput(title)
        label.GetTextProperty().SetFontSize(26)
        label.GetTextProperty().SetColor(0.1, 0.12, 0.15)
        label.GetTextProperty().SetJustificationToCentered()
        label.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        label.SetPosition(0.5, 0.93)
        renderer.AddViewProp(label)
        window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "build" / "cord-brace")
    args = parser.parse_args()
    config = load_config(args.config)
    args.output.mkdir(parents=True, exist_ok=True)

    _, local_sleeve, _ = _build_full_sleeve_shapes(config)
    parts = build_parts(config)
    sleeve_mesh = _mesh(local_sleeve, args.output / "sleeve-local.stl")
    items = [(sleeve_mesh, (0.20, 0.21, 0.23), 1.0)]
    scene = trimesh.Scene()
    scene.add_geometry(sleeve_mesh, node_name="sleeve")
    for name, shape in parts.items():
        mesh = _mesh(shape, args.output / f"{name}.stl")
        color = (0.93, 0.93, 0.93) if name == "dial" else (0.09, 0.09, 0.10)
        items.append((mesh, color, 1.0))
        rgba = np.array([*(round(c * 255) for c in color), 255], dtype=np.uint8)
        mesh.visual.face_colors = np.tile(rgba, (len(mesh.faces), 1))
        scene.add_geometry(mesh, node_name=name)
    rgba = np.array([51, 54, 59, 255], dtype=np.uint8)
    sleeve_mesh.visual.face_colors = np.tile(rgba, (len(sleeve_mesh.faces), 1))
    scene.export(args.output / "cord-brace-concept.glb")
    _render(args.output / "preview.png", items)
    print(f"wrote {args.output / 'preview.png'}")


if __name__ == "__main__":
    main()
