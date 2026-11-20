# Toolbox bins

Gridfinity bins traced from photos of Chris's tools with a self-hosted
[Tracefinity](https://github.com/tracefinity/tracefinity) (MIT, v0.10.1), driven
through its REST API by the scripts here. The web UI at http://localhost:3900 is
for checking and fixing traces by hand.

## Run

```sh
docker compose up -d          # Tracefinity on 127.0.0.1:3900, AUTH_MODE=open, isnet + inspyrenet
docker compose down
```

The tool library, bins and exports live in `data/`, and InSPyReNet's weights in
`model-cache/`. Both are gitignored, along with `build/` (runs, overlays, STLs).

## Photos

Lay the tools on the A4 dot-grid notebook (5 mm dots) and shoot from about 60 cm
straight down. At 28 to 30 cm Tracefinity warns that a 15 mm tool traces about
5.5% oversized. Keep your hands and the spiral out of frame where you can: the
spiral gets traced as a tool.

## Pipeline

```sh
# upload -> dot-grid corners -> flatten as A4 -> trace (default: isnet then inspyrenet)
scripts/run-grid.sh ~/Desktop/tool-photos/X.jpg build/runs/X
TRACER_LIST=inspyrenet scripts/run-grid.sh ...   # shiny/chrome tools

# draw the trace on the corrected photo with mm sizes
docker cp scripts/overlay.py tracefinity:/tmp/ && \
  docker exec tracefinity python3 -I /tmp/overlay.py <corrected.jpg> <trace.json> <scale> /tmp/o.jpg

# place tools in a bin (rotation, centre, per-tool pocket depth), then POST /api/bins/{id}/generate
python3 -I scripts/layout.py <bin_id> <grid_x> <grid_y> spec.json

# mesh check and preview
docker exec tracefinity python3 -I /tmp/meshcheck.py /tmp/bin.stl
nix develop -c uv run --no-project --with matplotlib --with trimesh python scripts/render.py out.png a.stl b.stl
```

### Why the dot grid instead of the paper outline

Tracefinity found no paper corners on 6 of 8 test photos (the spiral notebook on
white marble), and on the other 2 the corners it found were wrong. `grid_corners.py`
finds the printed dots, fits a homography from grid mm to image pixels (0.55 to
0.87 px rms across the 8 photos), and gives Tracefinity the corners of a virtual
A4 rectangle projected through it. The fitted A4 width matched the page edge, which
confirms the 5 mm pitch. This only works on the dot-grid notebook.

### Gotchas

- Bin auto-placement overlaps tools. `GET /bins/{id}` rebuilds each placed
  tool from the library, rotated by `rotation` about its centroid, at the placed
  centroid. `layout.py` writes it the same way so nothing moves.
- Pocket depth is one flat value per placed tool (`depth_override`). A sloped
  tool needs a stepped pocket: the same tool placed twice, with the deeper copy
  clipped to the low part.
- IS-Net bites into chrome edges. Use InSPyReNet for shiny tools.
- Interior holes are kept, so the gold razor's V gap becomes a post in its pocket.

### Far shots: mask outside the sheet

At 60 cm the sheet is small in the frame and Tracefinity's crop takes in the
counter. Unmasked, the saliency models traced the whole sheet or tools lying off
the paper in 5 of 5 photos. `scripts/run-masked.sh` replaces everything outside the
sheet with the paper's own shading (inpainted, so no edge is left), then
calibrates and traces. With that, InSPyReNet traced all 5 reshoot photos cleanly.
IS-Net still outlines the dotted area, so use InSPyReNet for far shots.

The loose sheet is the notebook page torn off its spiral: 282.75 x 211.05 mm
measured through the dot grid. It is not A4, so never pass Tracefinity's detected
corners with `paper_size: a4` directly: that stretches the long axis 5.3%.
`sheet_corners.py` maps them through the measured size instead, for photos where
the dots don't resolve.

The 60 cm traces came out 1 to 2% smaller on length than the close-ups, and up to
12% narrower on edge-on widths, as the close-up parallax warning predicted.
Library tools named `(60cm)` are the reshoot versions (`build/tool_ids_r2.txt`).

## Measurements

Caliper sheet: https://claude.ai/artifact/QZJPK2qWkNaubwZWpcjTeC (entries are in
its `measurements` and `notes` collections). The page source is
`scripts/caliper-sheet.template.html`, with its images inlined into `build/caliper-sheet.html`.

## Drawer (2026-11-05)

Drawer inside: 258.8 x 504.8 x 98 mm, so 6 x 12 Gridfinity cells.

**Baseplate** (`uv run --project projects/3d-printing/toolbox baseplate`, from the repo root in
`nix develop`): open frame, 4.65 mm tall, gridfinity-rebuilt socket profile. Bins
drop through to the drawer floor, so it adds no height. A 3.15 mm solid margin on
each long side takes up the spare width. The front and back edges are trimmed
0.5 mm, leaving 0.9 mm per end. It prints as two 258.3 x 251.5 mm halves for the
Plus 4 bed (53.3 cm3 each). Fit check: a generated bin seats on the floor with
zero overlap and 0.25 mm play per side.

**Bin** (Tracefinity, from tools fitted to the caliper sheet with `scripts/fit_tool.py`;
the safety razor handle widened to its 12.35 mm diameter with `scripts/widen_band.py`):
`build/print/razor-drawer-5x2x4u.stl`: all four tools nested in one 5x2 bin, 4u
(28 mm rim, 32.4 mm with the lip), plus an odds-and-ends box in the free corner.

Tracefinity's deepest pocket leaves the floor at z = 6.75 (4.75 foot + 2), so a
4u bin allows 21.25 mm. Pockets are standing height - 10 mm grab, capped at that:

| Pocket | Pose | Depth | Sticks up | Rotation |
|-|-|-|-|-|
| straight razor | on edge | 17.66 | 10.0 | 180 |
| safety razor | on edge | 21.25 (max) | 22.6 | 184 |
| nail clipper | flat | 9.09 | 10.0 | 180 |
| gold razor | flat, face up | 9.0 | 10.0 | 0 |
| odds and ends box | L around the right end, 3351 mm2, rounded | 21.25 (max) | - | - |

At 3u the straight razor would sit only half in its 14.25 mm slot. After the
packer, `scripts/slide.py` moved the safety razor 34.7 mm left (5 mm down, turned
4 degrees) so its handle fills the gap under the gold razor's handle. The box is
the free space left after keeping 5.5 mm from every tool and 5.35 mm from the bin
edge, with its corners rounded (3 mm): an L around the right end, about 80 cm3.
Top walls between pockets are at least 1.00 mm (2.0 mm and up below the chamfer),
with 0.15 mm to the lip at the tightest. Clearance 1.0 mm, chamfer 1.0 mm.
Watertight; the pocket floors measure at the depths above; 302 cm3. Tallest point
in the drawer: the safety razor head at about 50.6 mm.

The layout comes from `scripts/pack.py`: a raster bottom-left fill over 5-degree
rotations (and a mirror flip for the gold razor), trying every placement order, with
5 mm between outlines and 4.85 mm from the bin edge. 4x2 has no fit: after a
straight-razor row, the safety razor and clipper need 49.5 mm stacked beside the
gold razor's handle, and about 41.7 mm is left. A 264 mm2 sliver under the gold razor's V stays solid.
`scripts/plot_pack.py` draws a packing; `build/bn4-heightmap.png` is the generated bin.

## Status


Five tools are traced (`build/tool_ids.txt`), and there are two test bins:
`build/stl/vertical-slots.stl` (straight razor, safety razor and clipper standing on
edge; 4x2.5x6u; pockets 20/30/14 mm) and `build/stl/gold-razor-flat.stl` (2x4x4u, 15 mm).
Superseded by the drawer bins above. Nothing is printed yet.
