# BOA S2-S numbered seat gauges

The first plate is a **bench-only geometry check**, not a working receiver or
wearable closure. The photographs show two underside diameters (18.73 and
20.45 mm) and axial steps (1.15 and 2.21 mm), but not the snap-window undercut
well enough to design a trustworthy latch. The pocket order is a testable
assumption: if none of these seats, stop rather than forcing the BOA.

Generate the STL files from the repository root:

```sh
nix develop -c uv run --project projects/collar python -m collar.boa_seat_gauges
```

Print `build/boa-seat-gauges/boa-s2s-seat-gauges-1-to-4-plate.stl` in PLA,
flat side down, at 0.2 mm layers, with no supports. Each gauge is also exported
separately. The numeral is part of the STL. Do not scale the model in the
slicer. A brim should not be necessary for this small flat plate.

| Number | Added diameter clearance | Upper pocket | Lower pocket |
| --- | ---: | ---: | ---: |
| 1 | 0.10 mm | 20.55 mm | 18.83 mm |
| 2 | 0.30 mm | 20.75 mm | 19.03 mm |
| 3 | 0.50 mm | 20.95 mm | 19.23 mm |
| 4 | 0.70 mm | 21.15 mm | 19.43 mm |

Try the removable cartridge in numerical order with the laces in the side
reliefs. Record which one seats flat with light finger pressure, whether it
rocks, and whether the laces clear. **These gauges will not click or retain the
dial.** Do not twist, pry, or force the cartridge into a PLA gauge. Once the
seat geometry is confirmed, design a second small series to test the actual
snap tabs and release action before designing the collar mount.
