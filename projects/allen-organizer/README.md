# Allen-key organizer CAD

Parametric CadQuery tooling for holding a mixed metric/SAE allen-key collection,
sorted by size. Two designs share one config:

- **Slide tray (`allen-tray`)** — the current direction. Each long arm slides
  down a roofed channel; the short arm pokes straight out the front face through
  a guide slot whose walls stop the key rotating. Wall- or shelf-mountable,
  works vertical or flat. Built per row: a metric tray (13) and an SAE tray (9).
- **Staircase stand (`allen-stand`)** — earlier upright block. Kept for
  reference; keys can rotate in it, which is why the tray replaced it.

Every dimension comes from [`config/inventory.json`](config/inventory.json).
Bore diameter is derived in code as `key_mm + clearance_mm`, so the config holds
nominal key sizes, not pre-inflated hole sizes. Edit the table and re-run.

## Build

From the repository root:

```sh
nix develop -c uv sync --project projects/allen-organizer

# Slide trays: metric (13) and SAE (9), one row each.
nix develop -c uv run --project projects/allen-organizer allen-tray --tier metric_front
nix develop -c uv run --project projects/allen-organizer allen-tray --tier sae_back

# Overflow tray for duplicate working sizes (3 mm ×5, 4 mm ×2, 5 mm ×2, 3/32" ×4).
nix develop -c uv run --project projects/allen-organizer allen-spares

# Reference-only earlier design.
nix develop -c uv run --project projects/allen-organizer allen-stand
```

## Slide tray

`allen-tray --tier <name>` builds one row. Mechanism, per station:

- A teardrop channel runs along the tray; the long arm slides in. Teardrop top
  means the horizontal bore prints support-free (peak points up when the back
  face is on the bed).
- The channel is roofed except at the mouth, so a seated key can't lift straight
  out, only slide back along the channel.
- At the mouth the roof opens into a slot the width of the short arm. The short
  arm rises through it and pokes out the front face; the slot's side walls are
  the guides that keep it pointing straight out instead of spinning.
- Fixed channel depth (`channel_len_mm`): short keys sit fully inside, long keys
  protrude past the back edge (down, when wall-mounted).

Options: `--no-labels` drops the debossed sizes, `--no-mount` leaves the back
flat, `--no-svg` skips the preview, `--section <label>` emits a cutaway.

## Elfa mount

The back of each tray carries two dovetail sockets that slide onto the vendor
spring-clip from [thing:4060473](https://www.thingiverse.com/thing:4060473).
Print that `ElfaModuleClip.stl` (two per tray) and the clips lock into the
Utility Board; the tray slides down onto their bars and the clips' bottom stops
hold it.

- The socket profile is cloned from the vendor rack leg (`clip_saddle.py`
  constants), so it mates by construction: a 3.3 mm mouth widening to a 6.8 mm
  base over 6 mm, the undercut trapping the bar.
- Sockets sit a whole multiple of the **32.5 mm board slot pitch** apart
  (`mount.board_pitch_mm`), so both land on clips in adjacent slot columns.
- **Fit-test first:** `allen-saddle` builds `elfa-saddle-fit-test.stl`, one
  socket on a foot. Print it plus one clip and check the slide before the full
  tray. Retune with `allen-saddle --clearance 0.35` (looser) or `0.15` (tighter);
  the same `mount.clearance_mm` feeds the trays.

## Gotcha: cut overlapping cutters in separate passes

The channel and the short-arm slot overlap at each station. Putting both in one
`Compound` and cutting once makes the OCC boolean imprint the body into 13
per-station solids (a valid-looking but fragmented STL). Cutting channels in one
pass and slots in the next keeps it a single solid. Verify with
`len(result.val().Solids()) == 1`, not just `is_watertight`.

Artifacts land in `build/` and are not committed.

## Fit the clearance before the big print

The stand is ~208 mm wide and a multi-hour print. `allen-coupon` emits a handful
of slots (2/4/6/10 mm, 3/32", 1/4") so you can verify a key drops in snug but
pulls out by hand. Too tight → raise `clearance_mm`; too loose → lower it. The
stand and coupon read the same value, so tune once.

Options: `allen-coupon --labels 3 5 6` picks specific slots.
`allen-stand --no-labels` drops the debossed size text; `--no-svg` skips preview.

## Geometry notes

- Z-up, base on the plate at z=0. Bores open straight up, staircase steps face
  up: no supports, no bridging.
- Debossed size labels sit on each column's top face (top-layer text, reads from
  above). Label rendering is guarded; if the font engine fails headless it warns
  and exports without labels.
- Footprint ~208 × 58 mm, tallest column ~70 mm. Inside the QIDI Plus 4's
  305 × 305 × 280 mm envelope with room to spare.

## Printing

PLA+ is the easy default and plenty for a bench holder; PETG if it will sit in
sun or heat. Chamber heater off with the enclosure open for PLA/PETG per the
`3d-printing` brain layer. The block is modeled solid; let the slicer set infill
(~15%, 3 walls) rather than shelling it in CAD.
