# Nightstand bins

Gridfinity bins for the VAULT chest (`projects/tools/3d/vault/`) on the nightstand: trays on its
grid roof and in its drawers.

```sh
nix develop -c uv run --project projects/3d-printing/nightstand-bins nightstand-build [--only <part>]
```

STLs land in `build/`.

## Where the bins sit

The VAULT grid roof (7 x 5 cells) and baseplates (S5: 3 x 5, L5: 6 x 5) are plain 4 mm rib grids
on a 42 mm pitch, without the chamfered Gridfinity socket. Their holes are 37.3 mm at the bottom
and 38.3 mm at the top, so a foot's 37.2 mm straight section drops through and the upper taper
stops it on the rim. On a drawer baseplate the bin bottom ends up 0.85 mm above the box floor;
on the roof the feet reach the deck.

| Drawer | Floor to rim |
|-|-|
| S5 Box 2F | 82.5 mm |
| L5 Box 1F | 34.5 mm |

## Drawer trays

`drawer-tray-3x5-2u`: 3 x 5, 2u (14 mm to the wall top) with a gridfinity-rebuilt stacking lip,
18.4 mm overall. A second tray nests 14.05 mm higher, so stacked two high:

- the lower tray has 8.3 mm clear under the upper tray's feet; the top tray 12.65 mm to its lip
- the stack stands about 33.3 mm above the box floor, 1.2 mm under an L5 1F rim

One tray fills an S drawer; two side by side fill an L drawer (6 x 5). Sliced with `vault-pla`,
two trays on one plate are 4.5 h and 182 g (`build/print/N1 drawer trays/`).

## Roof (layout 3c)

The chest's back is near the wall and the bed is on its left. Front row first, as seen from the
drawer fronts:

| Part | Cells | Where |
|-|-|-|
| `roof-slot-block-2x5-6u` | 2 x 5 | left edge, full depth |
| `roof-tray-3x3-2u` | 3 x 3 | front, middle |
| `roof-tray-2x3-2u` | 2 x 3 | front, right |
| `roof-tall-3x2-6u` | 3 x 2 | back, middle |
| `roof-watch-dish-2x2-3u` | 2 x 2 | back, right; cable slot in the back wall |

The slot block holds the phone (15 mm in its case) in a 17 mm slot by the bed and the iPad
(14 mm in its case, 254 x 184 mm) in a 16 mm slot beside it. Both are 28 mm deep and lean 10
degrees right, so the screens tip toward the bed. The iPad slot is open at the front only, so the
iPad stands on its long edge and overhangs the front by 47 mm (about 37 mm past the roof edge);
put it in port-forward. A cable channel runs down the right side of the block.

Two cable catches sit on a ledge that hangs 21 mm (half a cell) off the back of the block, behind
the channel: a 5 mm slot open to the back and the top for the 4 mm cable, under a 13 x 7.5 x 8 mm
pocket that holds the plug's 12 x 6.5 mm molded head. The roof runs about 10 mm past the bin's back
edge, flat at deck height, so a catch inside the footprint bent the cable over the roof edge (the
first test piece); on the ledge the cable hangs about 5 mm clear of it. The ledge's underside rises
at 45 degrees from the back wall, so it prints without support and clears the roof by about 19 mm
at its edge. It stands 11 mm proud of the roof, so leave about 15 mm between the chest and the wall.

`roof-slot-test-2x1-6u` is the back cell of the block on its own, slots, ledge and catches, for
fit tests.

All five fit one plate: 8.2 h, 340 g (`build/print/N2 roof 3c/`).
