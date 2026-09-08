# Posture collar CAD

The project is intentionally gated. The scan-derived flexible inner sleeve must
be fitted and approved before any rib, strap, ratchet, or attachment geometry is
designed.

## Current milestone: sectional sleeve fit gauges

The source scan uses meters and includes the head and shoulders. The tooling
normalizes it to millimeters, takes horizontal neck sections, offsets those
sections by a configurable clearance, and exports short C-shaped fit gauges.
These small TPU prints let us tune fit without repeatedly printing a full
sleeve.

Each section is mirrored around its own left/right centerline by averaging the
two side widths at every posterior/anterior position. This removes scan and pose
asymmetry without flattening the throat or posterior neck profile. In the SVG
preview, dashed gray is the raw scan, dark gray is the symmetric section, blue
is the clearance surface, and red is the outside wall.

From the repository root:

```sh
nix develop -c uv sync
nix develop -c uv run --project projects/collar collar-scan-info
nix develop -c uv run --project projects/collar collar-fit-gauges
```

Generated artifacts go under `projects/collar/build/` and are not committed.
STLs are exported Z-up on a flat rim for slicing. STEP files retain the scan's
Y-up coordinate system so later sleeve and assembly geometry stays registered.

The initial landmark and fit values are deliberately provisional. Review the
generated section preview and test the gauges on the scan/mannequin before any
human fit check. A neck-worn device must never interfere with breathing or
swallowing, and ratchet tension is outside this milestone.
