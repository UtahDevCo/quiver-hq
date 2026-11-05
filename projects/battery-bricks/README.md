# Battery bricks CAD

Parametric CadQuery Gridfinity bricks for AAA, AA, 18650 and 21700 cells. Each brick
carries Gridfinity feet on two faces: its big face for a flat drawer (cells point up)
and one long edge for a three-high stack on Chris's 18° tilted shelf (cells point out,
bores run downhill so gravity seats them). Crush ribs in every bore stop rattle.

Design page: https://claude.ai/artifact/4uiQFJz8hW4G7GopDJshP1

## Build

```sh
# Fit coupon first: one bore per cell size at three rib squeezes (rows 1-3).
nix develop -c uv run --project projects/battery-bricks bricks-coupon --svg
# The three bricks, or name some: brick-aa brick-18650 brick-21700
nix develop -c uv run --project projects/battery-bricks bricks
# Shelf cradle: receivers for the bottom brick plus the lean-to frame to the wall
nix develop -c uv run --project projects/battery-bricks bricks-cradle
```

STLs land in `build/` (gitignored).

## Fit coupon

Rows 1, 2, 3 put the rib tips at nominal diameter minus 0, 0.2 and 0.4 mm. Push a real
cell of each size into each row. Pick the row where the cell slides in with light
finger pressure and doesn't fall out upside down. That squeeze goes into the bricks.
Print it in the same filament the bricks will use.

Coupon result (2026-11-04, PLA): AAA and AA row 2, 18650 row 1, 21700 tight even in
row 1, so it runs 0.2 mm looser. The squeezes live in `cells.py`.

## Printing

Big feet down, no supports. With 0.2 mm layers, 10% gyroid and 3 walls, the AA brick
is 186 g and 7 h 51 m. Five walls made it 238 g. Closed voids behind the lanes and
under the bores made it heavier (251 g at 5 walls), because each void gets its own
walls, so the bricks stay solid and the wall count is the lever.

The cradle prints standing on its base, no supports: 161 g and 7 h 29 m at the same
settings. It is 260 mm tall, inside the Plus 4's 280 mm. Shelf numbers it assumes
(depth 177.8 mm along the slope, 18°) are at the top of `cradle.py`.
