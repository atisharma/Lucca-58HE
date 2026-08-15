# /src/lucca/ - Lucca 58HE Build

Building a no-LED Lucca 58HE split Hall Effect keyboard.

## Context

- Repo: https://github.com/atisharma/Lucca-58HE (forked from Maka8295)
- 58-key (29/side) Hall Effect split keyboard, KMK firmware (CircuitPython)
- Upstream author unresponsive, no other known builds
- Build plan: `PLAN.md`

## Key Facts

- 29 sensors per side: 27x SOT-23 + 2x "1.5U HEKey" footprints (H25, H26).
- KiCad has no schematic (.kicad_sch), only PCB files (.kicad_pcb, KiCad 8 format)
- Component values are missing from KiCad: all resistors say `R_0805_...`, all caps say `C`
- PCB value field says HX6659ISO-B (Huaxin, LCSC C495742), README says DRV5053VAQDBZR. Both SOT-23, pin-compatible. HX6659 is in JLCPCB catalogue.
- Resistor values (per side): ~29x 1.5k (sensor LPF), ~2x 4.7k (I2C pull-ups), ~few 0R (UART jumpers). Exact assignment needs net tracing.
- For no-LED build: skip all SK6803/SK6812 LED footprints (29+10 per side), remove LED extensions from firmware.
- Gerbers in `PCBs/{left,right,plate}.zip` are fabrication-ready.
- Firmware cleanup needed: remove RGB extensions from code.py, fix pinout import (YD_RP2040 -> waveshareRP2040zero), strip neopixel.py.
- RP2040 Zero and USB-C connector are through-hole; JLCPCB won't place them. Solder by hand.

## Conventions

- British spelling
- ASCII only in code and text files
- No premature action -- discuss first
