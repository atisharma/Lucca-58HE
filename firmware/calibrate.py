# Lucca 58HE raw-ADC calibration helper.
#
# Copy this file onto a half's CIRCUITPY drive alongside kb.py, then run it
# (open the serial REPL and `import calibrate`, or temporarily rename it to
# code.py). It reuses the pin constants from kb.py for the current half, so it
# always matches the firmware pinout automatically.
#
# WHAT IT DOES
#   Sweeps the 32-channel mux, reads the raw 16-bit ADC (0..65535) on board.GP27
#   (the same pin analogio.py uses), and tracks the running MIN and MAX seen on
#   each channel. It prints a paste-ready block every PRINT_S seconds:
#
#       input_range = [
#           [max, min], [max, min], ...   # channel 0 .. 31
#       ]
#
#   callibration.py's `input_range` list is indexed [input_max, input_min]
#   (max first), which is what mapping() in analogio.py expects. For DRV5053
#   with the author's magnet orientation, REST is the HIGH value and PRESSED
#   is the LOW value -- so max=rest, min=pressed. Each entry is [rest, pressed].
#
# HOW TO USE
#   1. Boot the half with keys at rest. Let it print a few cycles untouched.
#      The MAX per channel settles to the rest value.
#   2. Slowly press and fully release every key, one at a time, across the whole
#      grid. The MIN per channel captures the fully-pressed value.
#   3. Stop the REPL (Ctrl-C) and copy the last printed left/right block into
#      callibration.py. Left half fills indices 0..31; right half fills 32..63.
#
# The board has only 29 sensors but the mux is 32:1, so channels for the 3
# unused mux inputs read floating garbage (erratic, not stable high/low).
# Ignore those 3 channels when pasting -- leave them as [14000, 1200].

import analogio
import digitalio
import time
from kb import KMKKeyboard  # class attrs only, no instantiation

READ_PIN = KMKKeyboard.read_pin
CTRL_PINS = KMKKeyboard.ctrl_pins          # 5 GPIOs (mux select)
CHANNELS = KMKKeyboard.mux_in_pins          # 32
PRINT_S = 2.0                                # seconds between prints
SETTLE_S = 0.0002                            # mux settle delay before reading

_read = analogio.AnalogIn(READ_PIN)
_ctrl = [digitalio.DigitalInOut(p) for p in CTRL_PINS]
for _p in _ctrl:
    _p.direction = digitalio.Direction.OUTPUT

_BITMASKS = (0b00001, 0b00010, 0b00100, 0b01000, 0b10000)


def read_channel(i):
    for _k, _mask in enumerate(_BITMASKS):
        _ctrl[_k].value = bool(i & _mask)
    time.sleep(SETTLE_S)
    return _read.value


def main():
    mn = [65535] * CHANNELS
    mx = [0] * CHANNELS
    last = time.monotonic()
    print("Lucca calibration: scanning", CHANNELS, "channels.")
    print("Step 1: leave all keys at rest for a few seconds (captures MAX).")
    print("Step 2: then slowly press+release every key (captures MIN).")
    print("Channel numbers are mux-channel order (matches input_range index).")
    while True:
        for i in range(CHANNELS):
            v = read_channel(i)
            if v < mn[i]:
                mn[i] = v
            if v > mx[i]:
                mx[i] = v
        now = time.monotonic()
        if now - last >= PRINT_S:
            last = now
            print("--- running [max, min] per channel (raw 0..65535) ---")
            line = "input_range = ["
            rows = []
            for i in range(CHANNELS):
                rows.append("    [{}, {}],".format(mx[i], mn[i]))
            print(line)
            for r in rows:
                print(r)
            print("]")
            print("rest(max) stable? press keys now if not yet. Ctrl-C to stop.")


if __name__ == "__main__":
    main()