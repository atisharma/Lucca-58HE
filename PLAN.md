# Lucca 58HE Build Plan

Building a no-LED Lucca 58HE split Hall Effect keyboard from
https://github.com/atisharma/Lucca-58HE (forked from Maka8295/Lucca-58HE).

## Project Summary

58-key (29 per side) Hall Effect split keyboard. Uses a 32:1 analog
multiplexer per side to read 29 HE sensors through a single ADC pin on
an RP2040 Zero. Firmware is KMK (CircuitPython). QMK port not yet
available.

The upstream author has one working prototype but is unresponsive to
issues. No other build reports exist. You will likely be the second
person to build this.

## Key Discoveries

### Sensor count resolved

The PCB has **29 sensors per side**:
- 27x SOT-23-3 footprints (standard key positions)
- 2x "1.5U HEKey" footprints (wider thumb keys, H25 and H26 on LHS)
- Both footprint types have `Value=HX6659ISO-B`
- 29 sensors = 29 keys per side.

### Sensor choice: HX6659ISO-B vs DRV5053VAQDBZR

The README BOM says DRV5053VAQDBZR. The KiCad `Value` field says
HX6659ISO-B. Both are SOT-23 linear Hall sensors and both are in the
JLCPCB catalogue -- but they are **NOT pin-compatible** (see below):

| Spec | DRV5053VA (TI) | HX6659ISO-B (Huaxin) |
|------|----------------|----------------------|
| Sensitivity | -40 mV/mT | ~25 mV/mT (2.5 mV/G) |
| Supply | 2.5V-38V | 2.8V-6V |
| Package | SOT-23 | SOT-23 |
| Pin 1 / 2 / 3 | VCC / OUT / GND | VCC / GND / OUT |
| JLCPCB part | C962159 (~$0.14) | C495742 (~$0.25) |
| Digikey | In stock, marked obsolete | Not checked |

The PCB was laid out for the DRV5053 DBZ pinout (pads 1/2/3 =
VCC/OUT/GND). The HX6659 swaps pins 2 and 3, so installing it would
short the mux input to GND. **Use DRV5053VAQDBZR only.**

This is not just a preference -- the PCB is laid out for the
DRV5053 DBZ pinout and is **incompatible with the HX6659ISO-B**
despite both being SOT-23.

The PCB's SOT-23 footprints assign nets: pad1=VCC, pad2=Q_n (sensor
output -> LPF -> mux), pad3=GND. This matches the DRV5053 DBZ pinout
exactly (Pin1=VCC, Pin2=OUT, Pin3=GND). The HX6659ISO-B has Pin1=VCC,
Pin2=GND, Pin3=OUT -- pins 2 and 3 are swapped. Installing an HX6659ISO-B
would short the mux input net (Q) to GND via the part's pin-2 GND, and
route the part's output (pin 3) into the board's GND plane. The board
would not function without a footprint revision -- there is no respin.

The KiCad `Value=HX6659ISO-B` field on every sensor is therefore a
mislabel by the original author; the README BOM (DRV5053VAQDBZR) is
the part the PCB was actually designed for. Use DRV5053VAQDBZR.

Secondary note: DRV5053 is bipolar (output 1 V at 0 field, swings both
ways); HX6659 is unipolar totem-pole. The firmware calibration
placeholders [14000, 1200] (rest high) and the analogio threshold signs
were written for the DRV5053/author's magnet orientation, so DRV5053 is
the drop-in firmware choice as well.

### Resistor and capacitor values missing from KiCad

All 35 resistors have `Value=R_0805_2012Metric_...` (just the footprint
name). All 60 capacitors have `Value=C`. These need correct values for
BOM/CPL generation.

**Verified by net tracing** -- each footprint's `(pad ... (net N "name"))
field was extracted from the `.kicad_pcb` files and classified by which
two nets the resistor/cap bridges. No schematic needed; pads carry their
net assignments directly.

#### Resistors (per side)

| Role | Value | LHS refs | RHS refs | Nets (pad1 <-> pad2) |
|------|-------|----------|----------|----------------------|
| Sensor LPF (29x) | 1.5k | R1-R29 | R1-R29 | Qn <-> An (sensor out -> mux in) |
| I2C pull-up SDA | 4.7k | R32 | R32 | VCC <-> SDA |
| I2C pull-up SCL | 4.7k | R33 | R31 | VCC <-> SCL |
| CS pull-up | 4.7k | R30 | -- (RHS uses a SJ, see below) | VCC <-> CS |
| SPI series jumper MOSI(L) | 0R | R31 | -- (SolderJumper) | MOSI(L) <-> MOSI(L) |
| SPI series jumper SCK | 0R | R34 | -- (SolderJumper) | SCK <-> SCK |
| SPI series jumper CS | 0R | R35 | -- (SolderJumper) | CS <-> CS |
| SPI series jumper MISO(L) | 0R | -- (LHS uses SJ) | R30 | MISO(L) <-> MISO(L) |

- **LHS totals**: 29 + 3 pull-ups + 3 SPI-series 0R = 35 resistors. Matches.
- **RHS totals**: 29 + 2 pull-ups + 1 SPI-series 0R = 32 resistors; the
  remaining 3 SPI lines carry solder jumpers (see below). Matches.
- The 1.5k + 100nF LPF gives fc ~= 1.06 kHz, appropriate anti-aliasing
  before the 12-bit ADC sampling the mux output.
- I2C (SDA/SCL) is routed to the OLED header -> do NOT populate the
  pull-ups if not using an OLED (KMK Split uses UART/SPI, not I2C). If
  populating OLED, fit R31/R32 (RHS) and R32/R33 (LHS).
- The LHS CS pull-up (R30, VCC<->CS) sits on CS, which is also one of
  the SPI inter-half lines. Its exact purpose is ambiguous from the
  netlist alone (could be a pull-up for inter-half CS, or for an SPI
  peripheral on the 4-pin header). For the no-LED/no-peripheral build,
  leave R30 DNP unless something genuinely needs CS pulled up. The RHS
  has no equivalent resistor (its CS line uses a solder jumper, kept
  open by default).

#### Capacitors (per side)

All 60 caps are C_0805 with `Value=C`. Net tracing groups them cleanly:

| Role | Qty/side | Value | Nets |
|------|---------|-------|------|
| Sensor LPF cap | 29 | 100nF | An <-> GND (one per sensor, pairs with the 1.5k R) |
| Decoupling / bulk | 31 | 100nF | VCC <-> GND |

- All 60 are 100nF 0805. The 31 VCC/GND caps decouple the 29 sensors
  (local decoupling near each sensor's VCC pin) + 1 for the mux +
  1 for the MCU module. One of the 31 is plausibly a larger bulk cap
  (e.g. 10uF), but since the footprint is uniform 0805 and there is no
  bulk-cap-elsewhere hint in the netlist, populate all 100nF. The MCU
  module (RP2040 Zero) has its own on-module decoupling so this is fine.

#### Solder jumpers (RHS only) -- configure SPI inter-half lines

| Ref | Footprint | Pads | Function |
|-----|-----------|------|----------|
| SJ (3-pad) | SolderJumper-3 | CS | MISO(L) | MISO(L) | selects CS vs MISO routing |
| SJ (2-pad) | SolderJumper-2 | CS | CS | bridges CS |
| SJ (2-pad) | SolderJumper-2 | CS | MISO(L) | CS <-> MISO link |

These configure the inter-half SPI/UART cable mode (see Open Q#6).
The LHS uses 0R resistors instead (R31/R34/R35) for the same lines.

### No schematic exists

Only `.kicad_pcb` files are available. No `.kicad_sch`, `.kicad_pro`,
or `.kicad_sym` files. This makes value assignment harder but not
impossible -- the PCB file contains net names that reveal circuit
topology.

Verified net names in the LHS PCB include: GND, VCC, A1-A29, SDA, SCL,
SCK, MOSI(L), MISO(L), CS, MulControl1-5, AIN1, LED1-29,
UGLED1-10, Q1-Q32.

### Gerber files are from an intermediate fork

The fork at `atisharma/Lucca-58HE` has Gerber zip files (`left.zip`,
`right.zip`, `plate.zip`) that are not in the original Maka8295 repo.
The KiCad PCB files are from the original. The Gerbers appear to have
been generated from the KiCad files without modification.

### PCB has solder jumpers (RHS only)

The RHS PCB has:
- 2x `SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm`
- 1x `SolderJumper-3_P1.3mm_Open_RoundedPad1.0x1.5mm`

These likely configure UART vs SPI inter-half communication mode. The
LHS uses a 0 Ohm resistor instead.

---

## Build Steps

### Phase 1: PCB Fabrication (can start immediately)

- [ ] Order bare PCBs from JLCPCB using existing Gerber zips
  - `PCBs/left.zip`, `PCBs/right.zip`, `PCBs/plate.zip`
  - 4-layer board, 1.6mm thickness
  - Order 5+ of each (minimum order)
  - **Surface finish: ENIG** (order-page dropdown; NOT a Gerber option).
    0.5mm-pitch TQFP-48 wants planar pads, castellated RP2040 Zero
    mounts wet reliably onto ENIG, and gold does not corrode on a board
    that gets touched for years. Single-digit-dollar premium at
    prototype qty. Avoid: leaded HASL (lead + domed pads), LF-HASL
    (domed pads), OSP (film burns off under the later hand-solder work).
  - **Solder mask: white** (choose for all three boards incl. plate --
    cost-neutral at JLC). White mask + black silkscreen + gold ENIG pads.
  - Everything else: factory defaults (1oz outer / 0.5oz inner copper,
    TG150, standard holes/vias, flying-probe test ticked). No high-spec
    options are justified -- see docs discussion; the board is
    logic-level, no impedance/VIPPO/heavy-copper need.

### Phase 2: Assembly Service Preparation

This is the main agent work. Goal: generate BOM and CPL files for JLCPCB PCBA.

- [ ] Assign correct values to all components in the KiCad PCB files
  - Trace resistor values from net names (1.5k near sensors, 4.7k near
    SDA/SCL, 0R near UART pins)
  - Verify capacitor values (likely all 100nF)
  - Confirm sensor part number in BOM (DRV5053VAQDBZR LCSC C962159 preferred; or HX6659ISO-B C495742)
  - Find LCSC part numbers for all components
  - Mark LED footprints as DNP (Do Not Populate) for no-LED build

- [ ] Generate BOM and CPL from KiCad
  - BOM: CSV with Reference, Value, Footprint, LCSC part number
  - CPL: CSV with Reference, X, Y, Rotation, Layer (Top/Bottom)
  - KiCad 8 can export both from the PCB editor

- [ ] Cross-reference against JLCPCB parts catalogue
  - Verify all parts are in stock
  - Note any parts JLCPCB doesn't carry (RP2040 Zero module -- through
    hole, solder yourself)

- [ ] Order PCBA from JLCPCB
  - Upload Gerbers, BOM, CPL
  - Select "Standard" PCBA (Economic tier does not accept 4-layer
    boards), single-side, bottom
  - Parts not in JLCPCB catalogue (RP2040 Zero) will be left unpopulated

### Phase 3: Manual Soldering (after PCBA delivery)

Only through-hole and parts JLCPCB can't place:

- [ ] Solder 2x Waveshare RP2040 Zero modules (through-hole, easy)
- [ ] Solder 2x USB-C connectors (through-hole, manageable)
- [ ] Solder OLED headers if using OLEDs (optional)
- [ ] Leave RHS solder jumpers OPEN for UART mode (they route the SPI
  inter-half lines; firmware uses UART, not SPI). Equivalently, leave the
  LHS 0R SPI-series resistors (R31 MOSI, R34 SCK, R35 CS) unpopulated.
  Bridging/populating them is only needed if you later switch firmware to
  `SplitType.SPI` and use the ribbon cable.

### Phase 4: 3D Printed Case

No local printer -- the case comes from **JLC3DP** (JLC's own print
service) so it can ride in the **same shipment as the PCBs/PCBA**
(one DDP delivery, no second shipping fee, and the case stops being
the long pole in the timeline).

- [ ] Upload `Case/Lucca58HE Case Left.stl` and `Lucca58HE Case Right.stl`
  to jlc3dp.com for an instant quote
  - **MJF PA12 (nylon)** -- better surface + durability for a case you
    handle daily; typically $10-30 for the pair, ~2 days
  - FDM PLA/PETG is the cheaper option (parts from $0.30 minimum) but
    visibly layer-lined
  - Choose "combine shipment" with the PCB/PCBA order at checkout
- [ ] Fallbacks: PCBWay 3D printing (second quote), a UK bureau via
  Craftcloud/Hubs (~GBP 20-50), or frameless (switch plate + PCB on
  the M2.5 standoffs, rubber feet -- no case at all)

### Phase 5: Firmware

- [ ] Flash CircuitPython 9.x onto both RP2040 Zero modules
  - Use `flash_nuke(1).uf2` first to clear, then
    `adafruit-circuitpython-waveshare_rp2040_zero-en_US-9.1.0.uf2`
    (both in repo root)

- [ ] Copy KMK firmware to CIRCUITPY drive
  - `kmk_firmware-main/kmk/` directory
  - `firmware/analogio.py` (custom AnalogScanner) -- copy this to
    `kmk/scanners/analogio.py` on CIRCUITPY, NOT the drive root
    (would shadow the built-in `analogio` module)
  - `firmware/callibration.py` (calibration values)
  - The upstream `boot.py` has been deleted from this fork. It configured
    `board.GP7` as a digital input with pull-up, conflicting with
    left-half mux control (`MulControl4`). Never restore it.

- [x] Clean up firmware for no-LED build  (DONE + verified, py_compile OK)
  - Removed both `RGB` extension blocks (imports + `under_rgb`/`rgb`
    objects + the two `keyboard.extensions.append` calls) from both
    `LEFT` and `RIGHT` `code.py`.
  - Deleted `neopixel.py` (only the RGB extension's lazy
    `import neopixel` used it; no longer triggered).
  - Fixed pinout import in both `firmware/left/kb.py` and
    `firmware/right/kb.py`: `YD_RP2040` -> `waveshareRP2040zero`.
    Verified that every pin index kb.py uses (read `pins[27]`=GP27; mux
    ctrl; tx/rx) maps to the SAME physical GPx in both quickpin files
    -- the swap is safe.
  - One-time fix only: the firmware is still author's 64-key `[14000,1200]`
    placeholders and 2-layer keymap with `XXXXXXX`; calibrate (Phase 6) and
    customise the keymap before final use.

- [ ] Customise keymap
  - Current keymap in `code.py` has some `XXXXXXX` placeholders
  - 2-layer layout currently defined
  - KMK keycodes reference: http://kmkfw.io/docs/

### Phase 6: Calibration and Testing

- [ ] Per-key calibration
  - `firmware/callibration.py` currently has placeholder values
    `[14000, 1200]` for all 64 keys (32 per side)
  - Need to read raw ADC values for each key at rest and fully pressed
  - Update the `input_range` list with actual min/max per key
  - May need to write a calibration script that reads and prints raw
    values

- [ ] Test actuation thresholds
  - `kb.py` has `actuation` with all values set to `1` (threshold mode)
  - Adjust per key for desired actuation point
  - Positive values = threshold mode, negative = rapid trigger mode
  - Rapid trigger code is present but commented out in `firmware/analogio.py`

### Phase 7: Assembly

- [ ] Install HE switches (Ati has Gateron Jades spare) into switch plate
- [ ] Place switch plate onto PCB
- [ ] Install PCB into 3D printed case
- [ ] Secure with M2.5 hardware (standoffs, screws, washers, nuts)
- [ ] Add keycaps
- [ ] Connect halves via USB-C cable (UART mode) or SPI ribbon cable

---

## BOM for No-LED Build (per side, x2 total)

| Component | Qty/side | Value | Package | LCSC | Notes |
|-----------|----------|-------|---------|------|-------|
| DRV5053VAQDBZR | 29 | HE sensor | SOT-23-3 + 1.5U Key | C962159 | Preferred; matches author's build. 27 SOT-23 + 2 in 1.5U footprint. (Alt: HX6659ISO-B C495742) |
| ADG732BSUZ | 1 | 32:1 mux | SU-48 / TQFP-48 | C579103 | In stock at JLC/LCSC |
| Resistor | 29 | 1.5k | 0805 | C4310 | LPF, one per sensor (R1-R29). LPF fc ~1.06 kHz |
| Resistor | 2 | 4.7k | 0805 | C17673 | I2C pull-ups SDA/SCL (LHS R32/R33, RHS R32/R31). **DNP for no-OLED build** |
| Resistor | 1 | 4.7k | 0805 | C17673 | CS pull-up (LHS R30 only). **DNP for no-peripheral build** |
| Resistor | 3 | 0R | 0805 | C17477 | LHS SPI-series 0R (MOSI R31, SCK R34, CS R35). **DNP for UART build** |
| Resistor | 1 | 0R | 0805 | C17477 | RHS SPI-series 0R (MISO R30). **DNP for UART build** |
| Capacitor | 29 | 100nF | 0805 | C1711 | Sensor LPF cap (on An) |
| Capacitor | 31 | 100nF | 0805 | C1711 | VCC/GND decoupling (sensors + mux + MCU) |

**Verified passive LCSC numbers** (all JLCPCB "Economic and Standard",
in stock, confirmed against JLC part-detail pages 2026-06-28):
1.5k=C4310, 4.7k=C17673, 0R=C17477, 100nF=C1711. Earlier
incorrect IDs (C17414/C17573/C17428/C1525) were discarded after
spot-checks showed wrong values/packages.

**For the confirmed no-LED / no-OLED / UART build the only POPULATED SMD
per side is: 29 sensors + 1 mux + 29x 1.5k (R1-R29) + 60x 100nF =
119 parts.** The 4.7k pull-ups, 0R SPI-series, LEDs, underglow, OLED
header, and solder jumpers are all DNP. The populated SMD is entirely
on the BOTTOM layer, so JLC's single-side assembly covers
it. (Economic PCBA is NOT available: it rejects 4-layer boards. Use
Standard, bottom side only.) Through-hole (RP2040 Zero, USB-C) is
hand-soldered. See `PCBs/assembly_README.md`.

### Hand-solder and optional parts

| Component | Qty/side | Value | Package | LCSC | Notes |
|-----------|----------|-------|---------|------|-------|
| RP2040 Zero | 1 | MCU module | Through-hole | N/A | Not in JLCPCB; solder yourself |
| USB-C (Molex) | 1 | 2137160001 | Through-hole | C5119949 | In catalogue, ~$1.55; JLC may not place TH -> hand-solder |
| OLED header | 1 | 4-pin 2.54mm | Through-hole | TBD | Optional -- OLED not implemented |

**Skipped (no-LED build):** 29x SK6803 MINI-E, 10x SK6812 underglow,
associated current-limiting components.

**Fasteners (total, both sides):**
- M2.5 brass standoffs 3mm
- M2.5 screws 12mm flat-top
- M2.5 washers 6x0.4mm
- M2.5 nuts 1.8mm

---

## Cost Estimate (no-LED / no-OLED / UART build, one full keyboard)

All figures USD, from JLC part-detail pages and JLC's PCBA price
article (2026-06-28). Prices are for the minimum practical order (one
keyboard = one LHS + one RHS board); unit prices fall steeply at higher
qty. **These are planning estimates -- the live JLC quote at upload time
is authoritative** (part prices change with stock and tier).

### JLC PCBA costs (both halves, single order)

| Item | How derived | Est. |
|------|-------------|------|
| DRV5053VAQDBZR sensors, 29/side x2 = 58 | 58 x $0.14 (C962159) | $8.12 |
| ADG732BSUZ mux, 1/side x2 = 2 | 2 x $10.10 (C579103) | $20.20 |
| 1.5k resistor, 29/side x2 = 58 | 58 x $0.0037 (C4310, 1+ tier) | $0.21 |
| 100nF cap, 60/side x2 = 120 | 120 x $0.0262 (C1711, 1+ tier) | $3.14 |
| **Parts subtotal (SMD, both sides)** | | **$31.67** |
| Standard PCBA setup | ~$25 / order (one order, both halves) | $25.00 |
| Stencil | $1.50 | $1.50 |
| Panel fee | $7.81 / panel | $7.81 |
| SMT assembly joints | 284 joints/side x 2 x $0.0016 | $0.91 |
| Hand-solder labour | $3.50 / order | $3.50 |
| X-ray inspection (AD72 mux is TQFP-48, has visible leads -> NOT BGA/QFN) | likely $0 | $0.00 |
| **JLC PCBA subtotal (excl. bare PCB)** | | **~$69.59** |

NOTE: JLC's cheaper Economic PCBA tier does NOT accept 4-layer boards,
and both halves are 4-layer -> Standard PCBA is the only option. All
populated SMD is on the bottom layer, so single-side placement is still
correct -- no double-side setup fee. Decline conformal coating (a
Standard-tier option): pointless for a desk keyboard, adds cost, and
makes the later hand-soldering and any rework harder.

### Bare PCBs (needed, fabricate+assemble in one JLC order)

- Board: ~133.4 x 100.2 mm per half, 4-layer, 1.6mm.
- JLC's advertised 4-layer promo and the size-bracket pricing mean each
  half is a few dollars per board at the 5-board minimum order (JLC's
  well-known $2/5-board deal is 2-layer 100x100mm; 4-layer and
  >100mm is higher). Budget ~$15-30 for all bare boards you'll receive
  (you'll get 5 of each half plus 5 plates as the minimum order).
- **Get the live bare-PCB quote at upload time** -- this is the line item
  most likely to move with board size and current JLC promos.

### Hand-solder parts (estimated, separate sourcing)

| Part | Qty | Each | Subtotal |
|------|-----|------|---------|
| Waveshare RP2040 Zero (JLC C5350143, in stock) | 2 | ~$3.90 | $7.80 |
| Molex USB-C 2137160001 (JLC C5119949) | 2 | ~$1.55 | $3.10 |
| **Hand-solder subtotal** | | | **$10.90** |

The RP2040 Zero is in JLC's catalogue as C5350143. JLC *can* place
castellated modules, but treating it as through-hole (hand-solder)
is the simplest path and what the PCB footprint expects. If you let
JLC place it, add the part to the BOM and a placement fee; it removes
the most fiddly hand-solder step.

### Non-JLC items (separate)

- Gateron Jade HE switches (~58 + spares): ~$1-2 each from vendors.
- Keycaps: varies widely.
- M2.5 fasteners (standoffs/screws/washers/nuts): a few dollars.
- 3D-printed case (STLs in `Case/`): ~$10-30 via JLC3DP MJF PA12,
  bundled into the same shipment.
- USB-C cable between halves (UART mode): standard data + charge cable.

### Bottom-line rough order of magnitude

| Bucket | Estimate |
|--------|----------|
| JLC PCBA (parts + assembly, both halves) | ~$53 |
| Bare PCBs (incl. plate, you keep 5 of each) | ~$15-30 |
| Hand-solder parts (2x RP2040 Zero + 2x USB-C) | ~$11 |
| **Electronics subtotal** | **~$80-95** |
| + switches, keycaps, fasteners, case, cable | varies |
| + JLC shipping (DHL/FedEx DDP to UK) | ~$15-25 |

For a single keyboard you are in the **~$100-120 landed electronics**
range before switches/keycaps/case. The AD732 mux (~$20 of the $53) is
the single largest line item; sensors (~$8) and bare boards are next.
Ordering 2-3 keyboards at once amortises the per-order setup fees
($8 + $1.50 + $3.50 = $13 fixed) and drops marginal cost sharply.

## Production Timeline (estimate)

After uploading Gerbers + BOM + CPL to JLC and paying:

| Stage | Typical |
|-------|---------|
| Bare PCB fabrication | 2-5 business days (24h express available) |
| Standard PCBA assembly | 3-5 business days after PCB fab |
| JLC QC + ship prep | 1-2 days |
| Carrier transit (DHL/FedEx to UK, DDP) | 3-7 days |
| **Order placed -> boards in hand** | **~2-3 weeks** |

Add on your side after delivery:
- Hand-solder RP2040 Zero + USB-C: ~1-2 hours.
- Flash CircuitPython + copy firmware + run `firmware/calibrate.py` +
  paste into `firmware/callibration.py`: ~1 hour.
- 3D-print case: comes in the same JLC shipment (MJF PA12, ~2 days fab
  at JLC3DP) -- no longer the long pole.
- Switch/keycap install + mechanical assembly: ~2 hours.

**Plan for ~3-4 weeks total** from order to a fully assembled, working
keyboard; ENIG finish and JLC3DP add dollars, not days.

Caveats: (1) larger 4-layer boards and current JLC promos move the
bare-PCB line; (2) PCBA lead time is for in-stock basic/extended parts
-- all our parts were in stock as of 2026-06-28 but verify at upload;
(3) JLC's CPL rotation must be eyeballed in the upload preview (see
`PCBs/assembly_README.md`) and corrected if the overlay shows a wrong
orientation -- a wrong rotation can mean a re-spin if the parts arrive
soldered backwards, especially for the ADG732 and the SOT-23 sensors.

---

## File Map

Repo cloned at: (re-clone from https://github.com/atisharma/Lucca-58HE)

Key files:
- `README.md` -- BOM, features, status
- `PCBs/Lucca1.0.kicad_pcbLHS.kicad_pcb` -- Left PCB (KiCad 8)
- `PCBs/Lucca1.0.kicad_pcbRHS.kicad_pcb` -- Right PCB (KiCad 8)
- `PCBs/Lucca1.0.kicad_pcbNewKey.kicad_pcb` -- Unknown (possibly a
  single-key test board)
- `PCBs/left.zip` -- Left Gerbers (fabrication-ready)
- `PCBs/right.zip` -- Right Gerbers (fabrication-ready)
- `PCBs/plate.zip` -- Switch plate Gerbers
- `PCBs/bom_net_trace.csv` -- Per-reference value + the two nets each R/C
  bridges (extracted from `.kicad_pcb` pad fields). Provenance for the
  resistor/cap values in this plan.
- `PCBs/inventory_full.csv` -- Full per-footprint classification (populated /
  DNP / manual / skip) for both sides.
- `PCBs/bom_lhs.csv`, `PCBs/bom_rhs.csv` -- JLCPCB BOM (populated SMD only).
- `PCBs/cpl_lhs.csv`, `PCBs/cpl_rhs.csv` -- JLCPCB CPL (positions, Layer=B).
- `PCBs/assembly_README.md` -- How to use the above for the JLC order, plus
  the rotation-verification caveat (the one step that needs the JLC uploader).
- `firmware/calibrate.py` -- Standalone raw-ADC calibration helper (A6).
  Copy onto a half's CIRCUITPY, run, press keys, paste the printed
  `input_range` block into `firmware/callibration.py`
  (left -> indices 0-31, right -> 32-63).
- `Case/Lucca58HE Case Left.stl` -- Left case
- `Case/Lucca58HE Case Right.stl` -- Right case
- `firmware/left/kb.py` -- Left keyboard definition (pinout, matrix)
- `firmware/left/code.py` -- Left keymap + extensions (RGB removed)
- `firmware/right/kb.py` -- Right keyboard definition
- `firmware/right/code.py` -- Right keymap + extensions (RGB removed)
- `firmware/analogio.py` -- Custom AnalogScanner for KMK (reads mux +
  sensors). Must be copied to `kmk/scanners/analogio.py` on CIRCUITPY,
  not the drive root (would shadow the built-in `analogio` module).
- `firmware/callibration.py` -- Per-key ADC min/max calibration values
- `flash_nuke(1).uf2` -- RP2040 flash eraser
- `adafruit-circuitpython-waveshare_rp2040_zero-en_US-9.1.0.uf2` --
  CircuitPython firmware
- `kmk_firmware-main/` -- Bundled KMK firmware (its
  `kmk/quickpin/RP2040/waveshareRP2040zero.py` provides the pinout; the
  old repo-root `quickpin/` duplicate was removed)

---

## Open Questions

1. **Resistor exact values and positions** -- RESOLVED. Every
   resistor/cap's two nets were extracted from the PCB pad fields. See
   the "Resistor and capacitor values" section above for the full
   per-reference table. (29x 1.5k LPF, 2x 4.7k I2C pull-ups, 1x 4.7k
   CS pull-up on LHS, 3x 0R SPI-series on LHS / 1x 0R + 3 SJ on RHS.)

2. **Decoupling capacitor values** -- RESOLVED. 29x 100nF sensor LPF
   caps (on An), 31x 100nF VCC/GND decoupling. Populating all 31 as
   100nF is safe; the MCU module has its own on-module bulk caps.

3. **ADG732 JLCPCB availability** -- RESOLVED. ADG732BSUZ is stocked
   in the JLC/LCSC catalogue as C579103, ~$10, in stock. JLCPCB can
   place it (TQFP-48, not QFN, so hand-soldering is a feasible fallback).

4. **RHS resistor count** -- RESOLVED. RHS has 32 resistors (29 LPF
   + 2 I2C pull-ups + 1 SPI-series 0R on MISO). The 3 lines LHS handles
   with 0R (MOSI/SCK/CS series) are instead 3 solder jumpers on RHS,
   accounting for the 35 vs 32 difference cleanly.

5. **USB-C connector JLCPCB availability** -- RESOLVED. Molex
   2137160001 is stocked as C5119949, ~$1.55. It is through-hole; JLC's
   economic assembly may not place through-hole parts, so plan to
   hand-solder it (as already noted in Phase 3).

6. **Inter-half cable** -- RESOLVED (firmware-default path). The shipped
   firmware uses `SplitType.UART` with `use_pio=True` on pins 12/13
   (`self.tx`/`self.rx`) on both halves (`firmware/{left,right}/kb.py`).
   **Follow the UART path for the initial build**: UART carries over the
   inter-half USB-C cable. The SPI lines (MOSI/MISO/SCK/CS) and their 0R
   series resistors / solder jumpers are for an optional SPI-ribbon mode
   that the firmware does NOT use by default -> leave all SPI-series 0R
   resistors unpopulated and the RHS solder jumpers open. (If you later
   want SPI mode you re-populate/bridge them and swap the firmware Split
   type; not needed for now.) UART slave latency, if noticed, can be
   reduced by lowering `uart_interval` (currently 1).

7. **OLED support** -- Hardware footprints exist but firmware is not
   implemented. Safe to skip for initial build.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| JLCPCB can't source ADG732 | ~~Medium~~ Low | High -- can't hand-solder QFN-48 (footprint is actually TQFP-48, hand-solderable) | CONFIRMED in catalogue as C579103. Fallback: Digikey/DigiKey ships today |
| Wrong resistor/cap values | Medium | Medium -- board doesn't work correctly | Trace nets carefully; test with multimeter after assembly |
| Firmware bugs | Medium | Low -- author uses it daily | KMK is Python, easy to modify on-device |
| `active_layers` actuation bug | Low | Low -- latent while all actuation values are identical | `analogio.py` uses a stale `KMKKeyboard()` instance for threshold lookup; does not see layer changes. Fix if per-layer actuation is needed later. |
| PCB design errors | Low | High -- need new PCB revision | Author's prototype works; Gerbers should be OK |
| Soldering damage | Low | Medium -- replace component | PCBA handles the hard parts; only through-hole left |
