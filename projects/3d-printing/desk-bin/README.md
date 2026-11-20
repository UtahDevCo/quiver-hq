# Desk bin

A rounded-square desk trash can with a swing lid: a bucket, a lid ring that drops over its rim,
and a flap that pivots on two pins across the middle of the ring. A keel under the flap's axis
pulls it back level after you push trash through.

```sh
nix develop -c uv run --project projects/3d-printing/desk-bin desk-bin-build [--only <part>]
```

STLs land in `build/`, already turned for the bed. `assembly-preview` is for looking at, not printing.

## Size

Body 105 x 105 x 100.3 mm with 22.5 mm corners; 114.3 mm (4.5 in) tall with the lid on, 109.8 mm
square at the lid. About 1 L inside. Every dimension is a constant at the top of
`src/desk_bin/bin.py`; the lid opening and flap follow `BODY_W`.

The first print was 140 mm square and 114.3 mm tall (the very first cut was 174 mm, too big for
the desk). Its height was right; this version is 75% of its width and depth. The keel hangs about
37 mm below the rim, so keep the body above about 55 mm.

## Parts

| Part | Orientation | Notes |
|-|-|-|
| `body` | upright | 2 mm walls, 2.4 mm floor, 4 mm fillet at the foot |
| `lid` | upside down | the skirt prints on the thicker upper wall, so no support |
| `flap` | top face down | 2 mm plate, 37 g solid; keel and hubs point up |
| `pin` | lying on their flats | two per plate |

The flap prints solid so its centre of mass lands where the model puts it: 7.0 mm below the pivot,
with a 24 x 12 x 45 mm keel. Below about 3 mm, friction at the pins can hold the flap 10 to 15
degrees open (keels of 30 mm or less on this flap land at 1 to 3 mm). The 140 mm print's
26 x 14 x 58 mm keel put it 8.5 mm below and closed reliably, but looked oversized; the same keel
on this flap would put it 13 mm below.

Checked in CadQuery: the flap clears the lid ring and body at every angle from -90 to 90 degrees.

## Plates

Sliced for the Plus 4 in Generic PLA with `projects/tools/3d/slicer`, 0.20 mm Standard on the
textured PEI plate. Folders are under `build/print/`.

| Plate | Profile | Time | PLA |
|-|-|-|-|
| `D1 body + lid + pins` | `vault-pla` | 2.8 h | 140 g |
| `D2 flap (solid)` | `pla-solid` (100% infill) | 1.0 h | 36 g |
| `D3 everything (solid)` | `pla-solid` | 4.3 h | 206 g |

D1 and D2 together are 176 g and 3.8 h. D3 puts all four parts on one plate, but the slicer CLI
can't set infill per object, so the body and lid print solid too: 30 g and half an hour more for
one fewer plate swap.

## Assembly

1. Drop the flap into the lid ring with its hubs toward the two pin holes.
2. Push a pin through each hole into the hub. The pin turns in the lid (4.4 mm hole) and presses
   into the flap (3.9 mm bore); add a drop of CA if it's loose. An M4 x 16 screw self-taps into
   the bore if a printed pin breaks.
3. Set the lid on the body. It sits on the rim and fits any of the four ways round.
