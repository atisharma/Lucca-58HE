# Lucca 58HE -- JLCPCB assembly deliverables (no-LED, no-OLED, UART build)

Files in this directory for the **no-LED / no-OLED / UART** build:

| File | Purpose |
|------|---------|
| `bom_lhs.csv`, `bom_rhs.csv` | Bill of materials for JLCPCB PCBA upload (populated SMD only) |
| `cpl_lhs.csv`, `cpl_rhs.csv` | Component placement list (X/Y/layer/rotation, populated SMD only) |
| `bom_net_trace.csv` | Per-reference provenance: the two nets each R/C bridges (from `.kicad_pcb` pad fields) |
| `inventory_full.csv` | Full per-footprint classification (populated / DNP / manual / skip) |
| `left.zip`, `right.zip`, `plate.zip` | Gerbers (bare board + switch plate) |

## What JLC assembles (per side, x2 sides)

| LCSC | Part | Qty | Role |
|------|------|-----|------|
| C962159 | DRV5053VAQDBZR Hall sensor (SOT-23 DBZ) | 29 | H1-H29 |
| C579103 | ADG732BSUZ 32:1 mux (TQFP-48) | 1 | U1 |
| C4310 | 1.5k 0805 1% resistor | 29 | R1-R29 (sensor LPF) |
| C1711 | 100nF 0805 X7R 50V cap | 60 | C1-C60 (29 LPF + 31 decoupling) |

**119 populated SMD parts per side, 238 total.**

## What is NOT assembled -- hand-solder or leave open

- **Through-hole (hand-solder):** 1x Waveshare RP2040 Zero, 1x Molex 2137160001
  USB-C. (OLED 4-pin header is no-OLED -> do not fit.)
- **DNP -- do not populate:**
  - 39x SK6812MINI-E LEDs per side (29 per-key + 10 underglow) -- no-LED build.
  - I2C pull-ups: LHS R32/R33, RHS R31/R32 (4.7k) -- no OLED, no I2C traffic.
  - CS pull-up: LHS R30 (4.7k) -- no SPI peripheral on the no-peripheral build.
  - SPI-series 0R: LHS R31/R34/R35, RHS R30 -- firmware uses UART, not SPI.
  - RHS solder jumpers (3x) -- leave OPEN for UART.
  - OLED 4-pin pin header.

## Single-side (Economic) assembly is sufficient

All 119 populated SMD parts per side are on the **BOTTOM** layer (B.Cu). The only
top-side parts are through-hole (RP2040 Zero, USB-C, OLED header) or DNP
resistors. So JLC's single-side Economic tier can place everything -- no
double-side assembly fee required. Select "Economic" and the **bottom** side
when uploading.

## CRITICAL -- rotation must be verified in JLC's upload preview

The rotation values in `cpl_*.csv` are emitted directly by KiCad's
`kicad-cli pcb export pos`. They are the **mechanical baseline** but are NOT
guaranteed to match JLC's library part orientations:

1. JLC matches each placement to its LCSC part and applies JLC's OWN library
   rotation. KiCad and JLC footprint frames do not always agree, especially for
   the ADG732 (TQFP-48, pin-1 location) and the SOT-23 sensors.
2. For bottom-side parts there is an additional mirror convention; the raw
   KiCad rotation may need a per-footprint offset (commonly +180 degrees for
   some footprints).

**Before confirming the order**, step through JLC's online BOM/CPL preview and
visually confirm the pin-1 / orientation overlay for at least:
- the ADG732 mux (U1) -- pin 1 toward the correct corner,
- the DRV5053 sensors -- VCC on pad 1, OUT on pad 2, GND on pad 3 (see
  PLAN.md "Sensor choice" -- the board is wired for the DRV5053 DBZ pinout; an
  HX6659 will NOT work),
- a few 0805 passives (rotation is less critical for symmetric pads).

If the preview shows a wrong orientation, edit the Rotation column in
`cpl_lhs.csv` / `cpl_rhs.csv` and re-upload. This rotation correction is the
one step that cannot be automated from the PCB file alone -- it depends on
JLC's library, which only their uploader can show.

## How these files were generated (reproducible)

- `bom_net_trace.csv` and `inventory_full.csv`: parsed each footprint block in
  `Lucca1.0.kicad_pcbLHS.kicad_pcb` and `...RHS...`, extracted the
  `(property "Reference"/"Value")` and each pad's `(net N "name")`, and
  classified resistors/caps by which two nets they bridge. No schematic was
  needed -- KiCad 8 stores pad net assignments in the PCB.
- `cpl_*.csv`: `kicad-cli pcb export pos --units mm --side both` (KiCad 10),
  filtered to the 119 populated-SMD references per side, Layer mapped
  bottom->B.
- All passive LCSC numbers were verified against the JLC part-detail pages
  (C4310, C17673, C17477, C1711 -- all "Economic and Standard", in stock).

## Known limitation of inventory_full.csv

The reference `REF**` is shared by 16 footprints per side (15 mounting holes +
1 USB-C connector), so the CSV collapses them to a single row. This does not
affect `bom_*.csv` / `cpl_*.csv`, which key on the unique R/C/H/U1 references.