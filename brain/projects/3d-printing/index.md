# 3d-printing

Project knowledge for `projects/3d-printing`. Reachable from inside the folder as
`.brain/index.md`.

Chris's home 3D printing setup: **QIDI Plus 4** (enclosed CoreXY, actively heated
chamber, direct-drive bimetal hotend to 370°C, bed to 120°C), a **SUNLU**
filament dryer, and **Magigoo** bed adhesive. Filaments: PLA+, PETG, PETG-CF, TPU.

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

*Meta practices this project narrows, extends, replaces, or suspends. Empty.*

# Patterns

*Reusable approaches. Empty.*

# Workflows

*How to run a piece of work here. Empty.*

# Failure modes

*Things that look right here and are not. Empty.*

# Practices

* [plus-4-chamber-heat-off-for-pla-and-tpu](practices/plus-4-chamber-heat-off-for-pla-and-tpu.md) - An enclosed heated chamber cooks PLA into heat-creep clogs and starves part cooling; open the door and pull the glass top for PLA and TPU. Chamber heat is for ABS/ASA/PC/nylon/CF.
* [cf-filament-needs-dedicated-hardened-nozzle](practices/cf-filament-needs-dedicated-hardened-nozzle.md) - Carbon-fiber filament is abrasive and wears even the bimetal stock nozzle; a hardened nozzle is effectively mandatory for PETG-CF. Swapping materials on one nozzle also causes clogs.
* [dry-hygroscopic-filament-and-feed-from-dryer](practices/dry-hygroscopic-filament-and-feed-from-dryer.md) - TPU and PETG-CF are the most hygroscopic filaments Chris runs and re-absorb water fast; dry them, feed from the dryer as a heated dry-box, store sealed with desiccant.
* [magigoo-original-covers-all-four-and-is-a-petg-release-barrier](practices/magigoo-original-covers-all-four-and-is-a-petg-release-barrier.md) - Magigoo Original works for all four filaments; for PETG its grip-hot/release-cool film is a barrier that stops PETG ripping chunks out of the PEI plate.

# Modules

* [qidi-plus-4-hardware-profile](modules/qidi-plus-4-hardware-profile.md) - Enclosed CoreXY, 305×305×280 mm, direct-drive bimetal hotend to 370°C, bed to 120°C, 400W chamber heater to 65°C, dual textured PEI, Klipper + QIDI Studio.
* [plus-4-per-material-slicer-starting-settings](modules/plus-4-per-material-slicer-starting-settings.md) - Starting nozzle/bed/chamber/speed ranges for PLA+/PETG/PETG-CF/TPU. Community starting points; QIDI Studio's built-in presets are authoritative.
* [sunlu-dryer-schedule-per-material](modules/sunlu-dryer-schedule-per-material.md) - Drying temp/time per material. SUNLU S2/S4 cap at 70°C, which covers all four; E2's 110°C is only for high-temp engineering filaments.

# Invariants

*Rules with an executable check attached. Empty.*

# Decisions

*Choices made and why. Empty.*

# Gems

*Project-local patterns worth promoting to meta. Empty.*

