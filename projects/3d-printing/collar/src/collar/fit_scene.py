from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

from .config import DEFAULT_CONFIG, PROJECT_ROOT, load_config, resolve_project_path
from .full_sleeve import build_full_sleeve
from .scan import STL_RECORD, inspect_binary_stl


def _expanded_bounds(
    minimum: np.ndarray,
    maximum: np.ndarray,
    margin: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if np.any(margin < 0.0):
        raise ValueError("Fit-scene crop margins cannot be negative")
    return minimum - margin, maximum + margin


def _crop_scan_triangles(
    path: Path,
    triangle_count: int,
    scale_to_mm: float,
    crop_min: np.ndarray,
    crop_max: np.ndarray,
    chunk_size: int = 200_000,
) -> np.ndarray:
    """Load triangles whose bounding boxes touch the visualization crop."""
    records = np.memmap(
        path,
        dtype=STL_RECORD,
        mode="r",
        offset=84,
        shape=(triangle_count,),
    )
    source = records["vertices"]
    chunks: list[np.ndarray] = []
    for start in range(0, triangle_count, chunk_size):
        triangles = source[start : start + chunk_size].astype(np.float64)
        triangles *= scale_to_mm
        overlaps = np.all(
            (triangles.max(axis=1) >= crop_min)
            & (triangles.min(axis=1) <= crop_max),
            axis=1,
        )
        if np.any(overlaps):
            chunks.append(triangles[overlaps])
    if not chunks:
        raise ValueError("The fit-scene crop does not intersect the source scan")
    return np.concatenate(chunks)


def _vertex_cluster_proxy(
    triangles: np.ndarray,
    voxel_mm: float,
) -> trimesh.Trimesh:
    """Make a display-only proxy by averaging vertices in a regular grid."""
    if voxel_mm <= 0.0:
        raise ValueError("Fit-scene proxy voxel size must be positive")

    points = triangles.reshape((-1, 3))
    origin = points.min(axis=0)
    cells = np.floor((points - origin) / voxel_mm + 0.5).astype(np.int64)
    _, inverse = np.unique(cells, axis=0, return_inverse=True)
    vertex_count = int(inverse.max()) + 1
    counts = np.bincount(inverse, minlength=vertex_count)
    vertices = np.column_stack(
        [
            np.bincount(inverse, weights=points[:, axis], minlength=vertex_count)
            / counts
            for axis in range(3)
        ]
    )
    faces = inverse.reshape((-1, 3))
    valid = (
        (faces[:, 0] != faces[:, 1])
        & (faces[:, 1] != faces[:, 2])
        & (faces[:, 2] != faces[:, 0])
    )
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces[valid], process=False)
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def _vtk_polydata(mesh: trimesh.Trimesh):
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(np.asarray(mesh.vertices), deep=True))
    offsets = np.arange(0, 3 * len(mesh.faces) + 1, 3, dtype=np.int64)
    connectivity = np.asarray(mesh.faces, dtype=np.int64).ravel()
    cells = vtk.vtkCellArray()
    cells.SetData(
        numpy_to_vtkIdTypeArray(offsets, deep=True),
        numpy_to_vtkIdTypeArray(connectivity, deep=True),
    )
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(cells)
    return polydata


def _vtk_actor(mesh: trimesh.Trimesh, color: tuple[float, float, float], opacity: float):
    import vtk

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(_vtk_polydata(mesh))
    normals.ComputePointNormalsOn()
    normals.SplittingOff()
    normals.ConsistencyOn()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetOpacity(opacity)
    actor.GetProperty().SetInterpolationToPhong()
    actor.GetProperty().SetAmbient(0.24)
    actor.GetProperty().SetDiffuse(0.76)
    actor.GetProperty().SetSpecular(0.08)
    return actor


def _write_preview(
    output: Path,
    proxy: trimesh.Trimesh | None,
    sleeve: trimesh.Trimesh,
    crop_min: np.ndarray,
    crop_max: np.ndarray,
) -> None:
    import vtk

    background = (0.965, 0.972, 0.98)
    center = (crop_min + crop_max) / 2.0
    views = [
        ("Front / chin", np.asarray((0.0, 0.0, 1.0))),
        ("Left", np.asarray((-1.0, 0.0, 0.0))),
        ("Rear opening", np.asarray((0.0, 0.0, -1.0))),
        ("Isometric", np.asarray((1.0, 0.35, 1.0))),
    ]
    window = vtk.vtkRenderWindow()
    window.SetSize(2200, 650)
    window.SetMultiSamples(8)
    window.SetOffScreenRendering(1)

    for index, (title, direction) in enumerate(views):
        renderer = vtk.vtkRenderer()
        renderer.SetViewport(index / 4.0, 0.0, (index + 1) / 4.0, 1.0)
        renderer.SetBackground(*background)
        renderer.SetUseDepthPeeling(True)
        renderer.SetMaximumNumberOfPeels(100)
        renderer.SetOcclusionRatio(0.02)
        if proxy is not None:
            renderer.AddActor(_vtk_actor(proxy, (0.76, 0.63, 0.53), 0.38))
        sleeve_opacity = 0.76 if proxy is not None else 1.0
        renderer.AddActor(
            _vtk_actor(sleeve, (0.05, 0.29, 0.62), sleeve_opacity)
        )

        direction = direction / np.linalg.norm(direction)
        camera = renderer.GetActiveCamera()
        camera.SetFocalPoint(*center)
        camera.SetPosition(*(center + direction * 1000.0))
        camera.SetViewUp(0.0, 1.0, 0.0)
        camera.ParallelProjectionOn()
        renderer.ResetCamera()
        camera.Zoom(1.08)

        label = vtk.vtkTextActor()
        label.SetInput(title)
        label.GetTextProperty().SetFontSize(24)
        label.GetTextProperty().SetColor(0.08, 0.10, 0.14)
        label.GetTextProperty().SetJustificationToCentered()
        label.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        label.SetPosition(0.5, 0.94)
        renderer.AddViewProp(label)
        window.AddRenderer(renderer)

    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetScale(1)
    capture.SetInputBufferTypeToRGBA()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def build_fit_scene(config: dict, output: Path) -> dict:
    scan_path = resolve_project_path(config, config["scan"])
    report = inspect_binary_stl(scan_path, float(config["scale_to_mm"]))
    scene_config = config["fit_scene"]
    sleeve_shape, sleeve_metadata = build_full_sleeve(config)
    sleeve_bbox = sleeve_shape.BoundingBox()
    sleeve_min = np.asarray(
        (sleeve_bbox.xmin, sleeve_bbox.ymin, sleeve_bbox.zmin), dtype=float
    )
    sleeve_max = np.asarray(
        (sleeve_bbox.xmax, sleeve_bbox.ymax, sleeve_bbox.zmax), dtype=float
    )
    margin = np.asarray(scene_config["crop_margin_mm"], dtype=float)
    if margin.shape != (3,):
        raise ValueError("fit_scene.crop_margin_mm must contain X, Y, Z margins")
    crop_min, crop_max = _expanded_bounds(sleeve_min, sleeve_max, margin)

    print("cropping Melissa scan around sleeve...", flush=True)
    cropped = _crop_scan_triangles(
        scan_path,
        report["triangle_count"],
        float(config["scale_to_mm"]),
        crop_min,
        crop_max,
    )
    print(f"clustering {len(cropped):,} scan triangles...", flush=True)
    proxy = _vertex_cluster_proxy(cropped, float(scene_config["proxy_voxel_mm"]))

    output.mkdir(parents=True, exist_ok=True)
    proxy_path = output / "melissa-neck-chin-shoulders-proxy.stl"
    sleeve_path = output / "melissa-inner-sleeve-scan-coordinates.stl"
    scene_path = output / "melissa-fit-scene.glb"
    preview_path = output / "preview.png"
    sleeve_preview_path = output / "sleeve-preview.png"
    manifest_path = output / "manifest.json"

    proxy.export(proxy_path)
    cq.exporters.export(
        sleeve_shape,
        str(sleeve_path),
        tolerance=0.08,
        angularTolerance=0.15,
    )
    sleeve_mesh = trimesh.load_mesh(sleeve_path, process=False)
    proxy.visual.face_colors = np.tile(
        np.asarray((203, 178, 158, 105), dtype=np.uint8),
        (len(proxy.faces), 1),
    )
    sleeve_mesh.visual.face_colors = np.tile(
        np.asarray((24, 94, 168, 230), dtype=np.uint8),
        (len(sleeve_mesh.faces), 1),
    )
    scene = trimesh.Scene()
    scene.add_geometry(proxy, node_name="Melissa scan proxy", geom_name="Melissa")
    scene.add_geometry(
        sleeve_mesh,
        node_name="Controlled-flare sleeve",
        geom_name="Sleeve",
    )
    scene.export(scene_path)
    _write_preview(
        preview_path,
        proxy,
        sleeve_mesh,
        crop_min,
        crop_max,
    )
    sleeve_margin = np.asarray((10.0, 10.0, 10.0))
    _write_preview(
        sleeve_preview_path,
        None,
        sleeve_mesh,
        sleeve_mesh.bounds[0] - sleeve_margin,
        sleeve_mesh.bounds[1] + sleeve_margin,
    )

    metadata = {
        "purpose": "visualization-only; original scan remains measurement truth",
        "coordinate_system": "millimeters, scan Y-up",
        "scan": report,
        "crop_bounds_mm": {"minimum": crop_min.tolist(), "maximum": crop_max.tolist()},
        "crop_margin_mm": margin.tolist(),
        "cropped_source_triangle_count": len(cropped),
        "proxy_voxel_mm": float(scene_config["proxy_voxel_mm"]),
        "proxy_vertex_count": len(proxy.vertices),
        "proxy_triangle_count": len(proxy.faces),
        "proxy_stl": str(proxy_path),
        "sleeve_stl": str(sleeve_path),
        "scene_glb": str(scene_path),
        "preview": str(preview_path),
        "sleeve_preview": str(sleeve_preview_path),
        "sleeve": sleeve_metadata,
    }
    manifest_path.write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Melissa's scan-and-sleeve visualization scene."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "build" / "fit-scene",
    )
    args = parser.parse_args()
    metadata = build_fit_scene(load_config(args.config), args.output)
    print(f"wrote {Path(metadata['scene_glb']).name}")
    print(f"proxy: {metadata['proxy_triangle_count']:,} triangles")


if __name__ == "__main__":
    main()
