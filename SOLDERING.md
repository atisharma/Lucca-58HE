# Lucca 58HE -- Hand-Soldering Notes

STATUS: hand-soldering the RP2040 Zero and USB-C is back ON. We tried
adding them to the JLC BOM as THT lines (J1/U2) on 2026-08-15; JLC
flagged both catalogue parts as assembly-shortage and asked for
substitution, so they were removed from the BOM instead. Substituting
module/connector parts risks footprint/pinout drift; hand-soldering
these four parts is the safer path.

All SMD (119 parts per side) is placed by JLCPCB. You hand-solder only **four components** for the entire keyboard: 2x RP2040 Zero + 2x Molex USB-C.

---

## Tools

| Item | Why |
|------|-----|
| Temperature-controlled iron, 60-80 W | Prevents overheating castellated pads and USB-C plastic |
| Chisel or hoof tip, 2.4 mm | Heat transfer for shield tabs and drag-soldering |
| Fine conical tip, 0.8-1 mm | USB-C signal pins if cleaning bridges |
| No-clean flux pen | More important than the iron brand; apply liberally |
| Solder braid / wick | Removes bridges between closely spaced USB-C pins |
| Brass wool tip cleaner | Avoids thermal-shocking the tip (damp sponges damage plating) |
| Leaded solder, 0.5-0.8 mm | Lower melting point, better flow than lead-free |
| Fine tweezers or probe | To nudge a pin upright before soldering |

---

## RP2040 Zero (castellated edge)

Each half uses one Waveshare RP2040 Zero. The footprint is through-hole in name, but the pads are actually **castellated edges** -- small half-moon holes along the module's edges.

### Placement

1. Check the PCB orientation: the USB-C connector on the module should face outward from the board, and the castellated side should sit flush against the matching edge pads.
2. Tack one corner pad to hold the module in place. Reheat and nudge until it is flat.
3. Drag-solder each of the four edges. Pre-flux the row, load the iron with a small bead of solder, and draw it steadily across the pads.
4. Inspect each pad for a fillet that connects the castellation to the PCB pad. Lacks of solder look shadowy; add a tiny touch if needed.
5. Check for bridges. At 1.27 mm pitch they are rare, but fix with flux + braid if they appear.

### Common mistake

Applying too much pressure or dwelling too long on a single pad lifts the module or overheats the pad. Keep contact under 2 seconds per pad. The iron temperature should be around 320-340 C.

---

## Molex USB-C Connector (2137160001)

This is a **through-hole** connector with sixteen signal pins in two rows plus four large shield tabs for mechanical retention.

### Pin layout

| Row | Pins | Pitch |
|-----|------|-------|
| A-side (back row) | A1, A4, A5, A6, A7, A8, A9, A12 | 0.85 mm |
| B-side (front row) | B1, B4, B5, B6, B7, B8, B9, B12 | 0.85 mm |

- **Row spacing:** 1.35 mm between A and B rows.
- **Drill:** 0.4 mm per signal pin.
- **Shield tabs (SH1-SH4):** Four oval through-hole pads at the corners. These provide mechanical strength and ground continuity.

### Recommended technique

1. **Solder the shield tabs first.** They are physically larger and hold the connector firmly against the board. Add flux, heat the tab and pad together for 2-3 seconds, then feed solder until the joint fills the oval. Do not force the connector flat while soldering -- if the board is slightly warped, hold it down with tweezers.
2. **Flux both rows of signal pins.**
3. **Drag-solder each row.** Load the chisel tip with a controlled bead of solder, then draw it smoothly across all eight pins in one pass. The 0.85 mm pitch is tight enough that bridges are likely; that is normal.
4. **Clean bridges with solder braid.** Lay a strip of braid over the bridged pins, press with the iron for 1 second, and lift. The braid wicks excess solder. Repeat between any bridged pairs.
5. **Inspect every pin.** A good joint shows a concave meniscus (fillet) around the pin. If a pin looks flat or shadowy, add a tiny touch of solder.

### Critical warning

Do not solder individual signal pins from above one at a time. The 0.4 mm holes and 0.85 mm pitch make cold joints and missed pins easy. Drag-soldering both rows in two passes, then cleaning with braid, is faster and more reliable.

Also, do not dwell on any single pin for more than ~2 seconds. The connector body is plastic and can soften or deform if overheated.

---

## What to leave alone

| Item | Action | Reason |
|------|--------|--------|
| OLED 4-pin header | **Do not fit** | No-OLED build |
| RHS solder jumpers (3x) | **Leave OPEN** | Firmware uses UART, not SPI |
| LED footprints (39 per side) | **Empty** | Already DNP by JLCPCB |
| RP2040 Zero USB-C | Keep clear after soldering | Do not short test probes against nearby passives |

---

## Post-solder checklist

- [ ] All four shield tabs on each USB-C have solid, shiny fillets with no voids.
- [ ] No solder bridges between adjacent USB-C signal pins (use a magnifier or phone macro lens).
- [ ] All castellated pads on RP2040 Zeros show solder wicking into the half-moon holes.
- [ ] USB-C connector sits flush against the PCB with no tilt.
- [ ] No loose flux residue inside the connector body (clean with isopropyl alcohol if needed).

After both halves are soldered and inspected, proceed to flash CircuitPython and copy the firmware (see `PLAN.md` Phase 5).
