# Posture collar CAD

A neck posture collar for Melissa, built from a scan of her neck: a TPU inner
sleeve that is printed and fits, and a PETG outer brace tightened by a
BOA-style dial. Everything here is parametric and regenerates from the scan,
`config/melissa.json` and the code. Current status and design decisions are in
`HANDOFF.md`.

From the repository root:

```sh
nix develop -c uv sync
```

Generated files go under `projects/collar/build/` and are not committed.

## Inner sleeve

```sh
nix develop -c uv run --project projects/collar collar-full-sleeve
```

Writes `build/full-sleeve/` (STL, STEP, 3MF). The sleeve uses the symmetric
`-47.5 mm` scan section as its fitted waist. It measures the neck centerline
across six nearby scan sections, projects the waist into a plane normal to that
axis, and builds a controlled hourglass around the resulting tilted local
frame: a 38 mm fitted centre band, 18 mm upper and lower transitions, and at
most 8 mm of radial flare. The skin-facing contour stays scan-derived, while a
low-frequency containing envelope smooths the outside into a clean surface for
the brace to bear on. It keeps a 24 mm rear opening.

Each scan section is mirrored around its own left/right centreline by
averaging the two side widths at every posterior/anterior position, which
removes scan and pose asymmetry without flattening the throat or the back of
the neck.

Supporting tools:

```sh
nix develop -c uv run --project projects/collar collar-scan-info   # scan bounds and units
nix develop -c uv run --project projects/collar collar-fit-gauges  # short C-shaped section gauges
nix develop -c uv run --project projects/collar collar-fit-scene   # scan + sleeve GLB, no Blender
```

## Outer brace

```sh
nix develop -c uv run --project projects/collar python -m collar.cord_brace    # sleeve-local.stl for the viewer
nix develop -c uv run --project projects/collar python -m collar.brace_parts   # printable parts, about 20 minutes
nix develop -c uv run --project projects/collar python -m collar.assembly_viz  # GLB + JSON for the 3D viewer
```

`brace_parts` writes `build/brace-parts/`: the anchor, five segments, the dial
pod and its lid as upright print STLs and STEPs, local-frame STLs, and
`report.json` with the joint, seam-stop and wall checks. Two paracords strung
through every part hold the chain together and act as its hinge line. The
dial closes the one seam between pod and anchor, and that seam's faces meeting
flush is the hard minimum-circumference stop.

Module map:

- `sleeve_profile.py`: the sleeve's smoothed outer profile, which every brace
  part is laid out on.
- `cord_brace.py`: layout and shape helpers shared by the parts.
- `dial_pod.py`: the pod's dial seat, lid, inserts and lace windows.
- `brace_parts.py`: joints, cord tunnels, knot pockets, the anchor's lace
  catch, and the checks.
- `assembly_viz.py`: export for the viewer and build-guide artifacts.

A neck-worn device must never interfere with breathing or swallowing. Validate
on a rigid stand-in first, and use only light tension for supervised fittings.
