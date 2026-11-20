# Desk bin

A rounded-square desk trash can with a swing lid: a bucket, a lid ring that drops over its rim,
and a flap that pivots on two pins across the middle of the ring. A keel under the flap's axis
pulls it back level after you push trash through.

```sh
nix develop -c uv run --project projects/3d-printing/desk-bin desk-bin-build [--only <part>]
```

STLs land in `build/`, already turned for the bed. `assembly-preview` is for looking at, not printing.

## Size

Body 140 x 140 x 100.3 mm with 30 mm corners; 114.3 mm (4.5 in) tall with the lid on, 144.8 mm
square at the lid. About 1.8 L inside. The first cut was 174 mm tall, which looked too big for the
desk. The flap's keel hangs about 50 mm below the rim, so keep the body above about 70 mm. Every dimension is a constant at the top of `src/desk_bin/bin.py`.

## Parts

| Part | Orientation | Notes |
|-|-|-|
| `body` | upright | 2 mm walls, 2.4 mm floor, 4 mm fillet at the foot |
| `lid` | upside down | the skirt prints on the thicker upper wall, so no support |
| `flap` | top face down | 2 mm plate, 64 g in PLA; keel and hubs point up |
| `pin` | lying on their flats | two per plate |

The flap's centre of mass sits 8.5 mm below the pivot if it prints solid, so it prints at 100%
infill. The first flap's sat 2.3 mm below, which friction at the pins could hold about 15 degrees
open. A 3 mm plate with a 60 x 18 x 45 mm keel fixed that at 9.2 mm but weighed 113 g; the 2 mm
plate with a 26 x 14 x 58 mm keel gets 8.5 mm for 63 g, so the flap fits on a partial spool.

Checked in CadQuery: the flap clears the lid ring and body at every angle from -90 to 90 degrees.

## Plates

Sliced for the Plus 4 in Generic PLA with `projects/tools/3d/slicer`, 0.20 mm Standard on the
textured PEI plate. Folders are under `build/print/`.

| Plate | Profile | Time | PLA |
|-|-|-|-|
| `D1 body + lid + pins` | `vault-pla` | 4.0 h | 199 g |
| `D2 flap (solid)` | `pla-solid` (100% infill) | 1.5 h | 63 g |

262 g and 5.5 h in all. The flap slices to 63 g against 64 g for the solid model, so the balance
figure above holds.

## Assembly

1. Drop the flap into the lid ring with its hubs toward the two pin holes.
2. Push a pin through each hole into the hub. The pin turns in the lid (4.4 mm hole) and presses
   into the flap (3.9 mm bore); add a drop of CA if it's loose. An M4 x 16 screw self-taps into
   the bore if a printed pin breaks.
3. Set the lid on the body. It sits on the rim and fits any of the four ways round.
