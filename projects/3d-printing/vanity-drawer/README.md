# Vanity drawer Gridfinity

CadQuery set for the bathroom vanity drawer: two baseplates, a razor shadow box,
and plain bins for everything else.

Drawer: 258.8 mm (10 3/16") wide at the floor, flaring to ~298 mm at the top,
508 mm (20") deep, 95 mm (3 3/4") clearance. That's a 6 by 12 Gridfinity grid
(252 by 504) with ~3 mm slack per side across and ~2 mm front and back.

## Build

From the repository root:

```sh
nix develop -c uv sync --project projects/3d-printing/vanity-drawer
nix develop -c uv run --project projects/3d-printing/vanity-drawer drawer-build
nix develop -c uv run --project projects/3d-printing/vanity-drawer drawer-build --only shadow-box
nix develop -c uv run --project projects/3d-printing/vanity-drawer drawer-build --layout-only
```

STLs and `layout.svg` (top-down plan, drawer front at the bottom) land in `build/`.
A full build takes about 15 minutes; use `--only <part>` while iterating.

## Parts

| Part | Grid | Height | Holds |
| --- | --- | --- | --- |
| baseplate-front, baseplate-back | 6x6 each | 4.65 | open frame, 2.4 mm side pads fill the drawer width |
| slot-box | 4x5 | 35 | comb, straight razor, knife, lighter, clippers, Feather blades, Leaf, DE razor, standing on their sides |
| brush-cradle | 2x3 | 40 | shave brush lying down |
| small-parts | 2x2 | 40 | open |
| shave-foam | 6x2 | 80 | foam can lying down |
| meds-body | 3x5 | 80 | Carpe, pill bottles, nasal inhaler |
| dental | 3x5 | 80 | floss, flossers, toothpaste, mouthwash, nail file |

Every part fits the QIDI Plus 4 bed (305 square). Layout and sizes live in
`config/drawer.json`.

## Slot box and brush cradle

`config/shadow.json` holds one footprint per item, in mm, per box. In the slot
box, items stand on their sides in lanes listed left to right. The build sizes
each lane to its widest item plus clearance, splits the leftover width into equal
walls (3.3 mm today), and fills each lane from the back. Pockets are offset 1 mm
outward and have flat floors.

Footprints are straight-sided simplifications of top-down photos of each item
resting on its side on 5 mm dot-grid paper (7.85 px/mm; dot grid and ruler
agree), rotated so the item's long axis runs along the slot.

- Straight razor 11.5 x 152, knife 17.2 x 111: the narrowest band that holds
  the whole trace.
- Comb (5 x 189), lighter (16 x 81), clippers (16 x 94) and the Feather pack
  (10 x 59) are measured rectangles. The comb and Feather pack are too thin and
  pale to trace, and the lighter was photographed upright.
- DE razor: a T, with a 13 mm handle and a 36 x 15.7 head.
- Leaf razor: its head pivots flat, so it lies in a shallow 12 mm pocket shaped
  as a symmetric Y (16 mm handle flaring to a 47 mm head), with a finger notch
  at the handle end.
- The brush cradle has two pocket depths (handle 18, knot 29.5) so the brush lies
  with its axis level. Its outline is hand-built from measured widths.

Fit-test cheaply first: in the slicer, cut the slot box about 8 mm below its top
and print only that slab to check the slot widths.
