# 3d-printing

A standalone project managed by the `quiver-hq` repo (no submodule of its own).
Home for 3D printing knowledge, slicer profiles, and models.

Hardware: **QIDI Plus 4** (enclosed CoreXY, actively heated chamber), **SUNLU**
filament dryer, **Magigoo** bed adhesive. Filaments in use: PLA+, PETG, PETG-CF,
TPU.

## Layout

- `profiles/` — slicer configs (QIDI Studio / Orca) per filament.
- `models/` — STLs and print-ready geometry.
- `notes/` — print logs, tuning notes, per-project settings.

CAD projects, each its own uv project (`nix develop -c uv run --project projects/3d-printing/<name> ...`):

- `allen-organizer/`: allen-key trays and stand.
- `battery-bricks/`: Gridfinity battery bricks.
- `collar/`: posture collar from a neck scan.
- `nightstand-bins/`: Gridfinity bins for the VAULT chest.
- `toolbox/`: tool-traced Gridfinity bins via a local Tracefinity (`docker compose up -d`, port 3900).
- `vanity-drawer/`: bathroom vanity drawer baseplates and bins.

## Knowledge

Durable engineering knowledge lives in the brain, reachable from here as
`.brain/index.md`. Recall it with `/brain-recall <topic>` while working in this
folder. The initial hardware/filament/adhesive research is in the brain inbox
pending `/brain-promote`.
