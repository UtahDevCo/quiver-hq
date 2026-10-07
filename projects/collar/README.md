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
Fit-gauge STLs are exported Z-up on a flat rim. The full-sleeve STL is exported
from its fitted local frame, with the neck axis mapped to print Z and the entire
lower C-shaped flare rim on the build plate. STEP files retain the scan's Y-up
coordinate system so later sleeve and assembly geometry stays registered.

After the sectional gauges identify a usable neck contour, generate the first
full-sleeve geometry prototype with:

```sh
nix develop -c uv run --project projects/collar collar-full-sleeve
```

The prototype uses the symmetric `-47.5 mm` scan section as its fitted waist.
It measures the neck centerline across six nearby scan sections, projects the
waist into a plane normal to that axis, and builds a controlled hourglass around
the resulting tilted local frame: a 38 mm fitted center band, shallow 18 mm
upper and lower transition zones, and at most 8 mm of radial flare. This follows
the reference collar's restrained edge rolls while avoiding the much wider
literal chin and shoulder scan intersections.
The skin-facing contour remains scan-derived, while a low-frequency containing
envelope smooths the outside into a clean brace interface. The envelope is
expanded only as much as necessary to retain the configured minimum wall, so
outer smoothness does not come at the expense of inner fit or wall thickness.
It retains the 24 mm rear opening used by the fit gauges. Melissa's
approximately 25.4 mm rear overlap observation is recorded in the
configuration but is deliberately not applied as a circumference correction
yet; this first full-height print is for checking the flare proportions without
ratchet tension.

Build a registered visualization of Melissa's scan and the prototype sleeve
without Blender with:

```sh
nix develop -c uv run --project projects/collar collar-fit-scene
```

This writes a cropped, vertex-clustered neck/chin/shoulder proxy, a sleeve STL
in the scan's millimeter Y-up coordinates, a colored GLB containing both
objects, an overlay preview, and a sleeve-only surface preview under
`projects/collar/build/fit-scene/`. The proxy is visualization-only; all
dimensional work continues to use the untouched high-resolution scan.

The initial landmark and fit values are deliberately provisional. Review the
generated section preview and test the gauges on the scan/mannequin before any
human fit check. A neck-worn device must never interfere with breathing or
swallowing, and ratchet tension is outside this milestone.

After approving the untensioned sleeve fit, generate a dimensional packaging
study for the segmented brace and measured ratchet hardware with:

```sh
nix develop -c uv run --project projects/collar collar-outer-brace
```

The concept uses eight 36 mm-tall guides around the sleeve's 38 mm smooth waist,
leaving clearance before both flare transitions. Complementary radial half-lap
tongues bridge the moving seams and conceal the underlying strap while allowing
the segments to slide together. Their tunnels clear the measured 19.19 mm by
3.9 mm toothed strap, and the scene includes the 65.58 by 30.4 by 30.36 mm
buckle envelope across the rear opening. This is a visualization gate, not yet
a wearable part: the buckle mount, positive tightening stop, emergency release
access, and load testing remain unresolved.
