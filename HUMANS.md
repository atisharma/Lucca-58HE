# HUMANS.md - Returning Guide for the Lucca 58HE Build

Read this when you come back after a break. It tells you the state and the
next action. For depth, read `PLAN.md` and `PCBs/assembly_README.md`.

## What this is

A no-LED, no-OLED, UART-mode Lucca 58HE: a 58-key (29/side) Hall-effect
split keyboard. Forked from Maka8295; the upstream author is unresponsive,
so you are effectively build number two. SMD is JLC-assembled; you
hand-solder the through-hole parts, flash firmware, calibrate, assemble.

## Current state (2026-06-28)

All design/agent work is **DONE**. The project is ready to order and build.
Nothing further needs the agent for design decisions (the firmware is the
author's, with LED blocks removed and pinout fixed; calibration values are
still placeholders until you run them on real hardware).

What is done: net-traced BOM, JLC BOM/CPL files, firmware cleanup,
calibration helper, cost/timeline estimate, docs.

What is NOT done (only you can do these): order, hand-solder, flash,
calibrate, mechanical assembly.

## Critical facts - do not forget

1. **Use DRV5053VAQDBZR (LCSC C962159), NOT HX6659ISO-B.** The KiCad
   `Value=HX6659ISO-B` field on every sensor is a mislabel by the original
   author. The PCB pads are wired 1=VCC, 2=OUT, 3=GND - the DRV5053 DBZ
   pinout. The HX6659 swaps pins 2/3 and would short the mux input to
   GND. There is no respin planned; only DRV5053 fits.
2. **Check the JLC CPL rotation in the upload preview before paying.**
   The `cpl_*.csv` rotations are KiCad's mechanical baseline. JLC matches
   by LCSC part number and applies its own library orientation. Eyeball
   the ADG732 mux (48-pin, pin-1 corner) and the SOT-23 sensors
   especially - a backwards-soldered part means a re-spin. Edit the
   Rotation column and re-upload if the overlay looks wrong. Full detail in
   `PCBs/assembly_README.md`.
3. **RHS solder jumpers stay OPEN. LHS 0R SPI resistors (R31/R34/R35) stay
   UNPOPULATED.** The firmware uses UART over the USB-C inter-half cable,
   not SPI. (Earlier drafts said "bridge for UART" - that was backwards;
   the plan is corrected.)
4. **No I2C pull-ups populated** (LHS R32/R33, RHS R31/R32). No OLED -> no
   I2C traffic -> DNP them.
5. **All populated SMD is on the BOTTOM layer.** Order single-side
   assembly, bottom side. No double-side fee needed. Economic PCBA drops
   out because ENIG is an Economic-restricted finish - use **Standard**
   tier. Assembly quantity 2 per side (JLC min; qty 5 triples the
   components cost, dominated by the ~$29 ADG732 mux per board).
6. **Surface finish = ENIG** (order-page dropdown at JLC; NOT a Gerber
   property). Planar pads for the 0.5mm TQFP-48 mux, reliable castellated
   mounting for the RP2040 Zero, no lead, no corrosion. Avoid leaded HASL
   and OSP (bad for the later hand-soldering). Single-digit-$ premium.
   **Solder mask: white** on all three boards (left, right, plate) --
   chosen for looks, cost-neutral. Everything else: factory defaults
   (1oz/0.5oz copper, TG150, standard vias, flying-probe test on).

## Returning checklist

### 0. Re-orient (5 minutes)

- [ ] Read this file.
- [ ] Skim `PLAN.md` (the BOM table, Cost Estimate, the phase you are at).
- [ ] If unsure of file provenance, open `PCBs/bom_net_trace.csv` - it lists
      what net every R/C bridges, which is how values were derived.

### 1. Verify nothing has drifted (10 minutes, before ordering)

- [ ] Check the 5 key parts are still in stock at JLC/LCSC (they were on
      2026-06-28 but parts go out of stock):
      DRV5053VAQDBZR C962159, ADG732BSUZ C579103, 1.5k R C4310,
      100nF C C1711, USB-C C5119949, RP2040 Zero C5350143.
- [ ] `python3 -m py_compile` on the four firmware files if you touched
      them - confirm still OK:
      `python3 -m py_compile firmware/left/code.py firmware/left/kb.py firmware/right/code.py firmware/right/kb.py firmware/analogio.py firmware/callibration.py firmware/calibrate.py`

### 2. Place the JLC order (Phase 1 + Phase 2 combined)

- [ ] On jlcpcb.com start a "PCB Assembly" order.
- [ ] Upload Gerber zip for LEFT: `PCBs/left.zip`.
- [ ] Upload `PCBs/bom_lhs.csv` and `PCBs/cpl_lhs.csv`.
- [ ] Select **Standard** PCBA (Economic drops out with ENIG),
      **bottom** side for placement. Decline conformal coating.
- [ ] Set **assembly quantity to 2 per side** (JLC min). Default qty 5
      costs ~$228/side in components; qty 2 is ~$92/side and keeps
      DRV5053 demand (58) inside LCSC's ~230 stock.
- [ ] **In the preview, walk through placements and verify rotations**
      (see critical fact #2). Fix and re-upload if wrong.
- [ ] Repeat as a second order (or same order, second board) for RIGHT:
      `PCBs/right.zip`, `PCBs/bom_rhs.csv`, `PCBs/cpl_rhs.csv`.
- [ ] Order the switch plate Gerbers too if you want them fabricated:
      `PCBs/plate.zip` (bare PCB, no assembly).
- [ ] Set surface finish to **ENIG** on the PCB quote page (critical fact
      #6 below). It is an order-page dropdown, NOT in the Gerbers.
- [ ] Add the case to the same shipment: upload
      `Case/Lucca58HE Case Left.stl` + `Right.stl` to JLC3DP, pick
      MJF PA12 (nylon), choose combine-shipment with the PCB order.
      (No local printer - this replaces that step.)
- [ ] Choose DDP shipping (DHL or FedEx) to the UK for predictable total.
- [ ] Pay. Expected landed time to your door: ~2-3 weeks.

### 3. Source hand-solder parts (parallel with the order)

- [ ] 2x Waveshare RP2040 Zero (LCSC C5350143, ~$3.90 each). (Tried JLC
      THT placement 2026-08-15; JLC reports assembly shortage, so
      hand-solder per SOLDERING.md.)
- [ ] 2x Molex USB-C 2137160001 (JLC C5119949, ~$1.55 each) - same,
      hand-solder.
- [ ] HE switches: Gateron Jades, ~58 + a few spares.
- [ ] Keycaps (whatever layout you want).
- [ ] M2.5 fasteners: 3mm brass standoffs, 12mm flat-top screws, 6x0.4mm
      washers, 1.8mm nuts.
- [ ] A USB-C data cable for the inter-half link (UART).

### 4. Hand-solder through-hole (Phase 3, after delivery, ~1-2 hours)

- [ ] Solder the 2x RP2040 Zero modules (one per board).
- [ ] Solder the 2x USB-C connectors.
- [ ] Do NOT populate: LEDs, underglow, OLED header, I2C pull-ups (R32/R33
      LHS, R31/R32 RHS), CS pull-up (R30 LHS), SPI-series 0R (R31/R34/R35
      LHS, R30 RHS).
- [ ] Do NOT bridge the RHS solder jumpers (they must stay open for UART).

### 5. Flash firmware (Phase 5)

- [ ] On each RP2040 Zero: hold BOOTSEL, plug USB, drag
      `flash_nuke(1).uf2` onto the RPI-RP2 drive to clear.
- [ ] Then drag `adafruit-circuitpython-waveshare_rp2040_zero-en_US-9.1.0.uf2`
      onto the drive. It reboots as CIRCUITPY.
- [ ] Copy to CIRCUITPY: `kmk_firmware-main/kmk/`, `firmware/analogio.py`,
      `firmware/callibration.py`, and either `firmware/left/kb.py`
      + `code.py` (renamed to `code.py`) or the RIGHT equivalents.
- [ ] Confirm the half boots and the serial REPL is reachable.

### 6. Calibrate (Phase 6, ~1 hour)

- [ ] Copy `firmware/calibrate.py` to each half's CIRCUITPY and run it.
- [ ] Leave keys at rest for a few seconds (captures the per-channel MAX).
- [ ] Slowly press and fully release every key one at a time (captures MIN).
- [ ] Copy the printed `input_range` block into `firmware/callibration.py`:
      LEFT half -> indices 0-31, RIGHT half -> indices 32-63.
- [ ] Ignore the 3 unused mux channels (they read floating garbage) - leave
      those as `[14000, 1200]`.

### 7. Final assembly (Phase 7, ~2 hours)

- [ ] Install HE switches into the switch plate.
- [ ] Place plate onto PCB.
- [ ] Drop assembly into the 3D-printed case.
- [ ] Secure with M2.5 standoffs/screws/washers/nuts.
- [ ] Add keycaps.
- [ ] Connect halves with the USB-C cable (UART).
- [ ] Plug the master half into your computer. Type.

## Quick file map

| File | Use |
|------|-----|
| `PLAN.md` | Full plan, BOM table, cost + timeline. The reference doc. |
| `README.md` | Upstream project intro + fork notes block at the top. |
| `PCBs/assembly_README.md` | How to use the BOM/CPL on JLC + rotation caveat. |
| `PCBs/bom_lhs.csv`, `bom_rhs.csv` | Upload these to JLC. |
| `PCBs/cpl_lhs.csv`, `cpl_rhs.csv` | Upload these to JLC. |
| `PCBs/bom_net_trace.csv` | Provenance: which two nets each R/C bridges. |
| `PCBs/inventory_full.csv` | Full per-part classification (populated/DNP/manual). |
| `PCBs/{left,right,plate}.zip` | Gerbers for bare boards. |
| `firmware/left/`, `firmware/right/` | Firmware halves (already cleaned, RGB removed). |
| `firmware/analogio.py` | KMK AnalogScanner (reads mux). |
| `firmware/callibration.py` | Per-key ADC min/max - you fill this from calibrate.py. |
| `firmware/calibrate.py` | The helper that prints min/max values to paste in. |
| `Case/*.stl` | Case STLs - upload to JLC3DP, MJF PA12. |

## If something does not work

- **No keys register on one half:** check the inter-half USB-C cable carries
  data (some charge-only cables lack the data pairs); check tx/rx pins on
  both halves (LHS uses pins 12/13, RHS uses 8/9 - already correct in kb.py).
- **One key reads wrong / floats:** likely the sensor on that key is
  backwards or the magnet orientation is off. DRV5053 output is ~1V at
  zero field and swings both ways - check the calibration entry for that
  channel.
- **Slave-half latency (the author noted this):** UART slave has some lag.
  Lower `uart_interval` in `kb.py`, or consider the SPI-ribbon mode (would
  need populating the 0R resistors and re-bridging the solder jumpers, and
  changing `SplitType.UART` to `SplitType.SPI`).
- **A populated SMD part came soldered backwards:** this is the rotation
  risk from critical fact #2. File a JLC rework/RMA; do not desolder the
  ADG732 yourself unless you have hot-air.

## Estimated all-in

Electronics landed (PCBA + bare boards + hand-solder parts + shipping to
UK): ~$100-120 before switches/keycaps/case. ~2-3 weeks order to door.
Full detail in `PLAN.md`, "Cost Estimate" and "Production Timeline".
