# Inky Frame 7.3 Spectra (Pico 2 W) Setup

This guide documents the steps taken to get a Pimoroni Inky Frame 7.3” Spectra (6-color) working with a Pico 2 W, using MicroPython and PicoGraphics.

---

## 1. Firmware Installation

1. Download the **correct Pimoroni Inky Frame firmware** for the Pico 2 W:

   ```
   pico2_w_inky-v1.26.1-micropython-without-filesystem.uf2
   ```

   *(Do not use the `-with-filesystem` version if encountering import issues.)*

2. Flash the firmware:

   1. Unplug the Pico 2 W
   2. Hold **BOOTSEL** and plug in USB
   3. Drag the UF2 file onto the `RPI-RP2` drive
   4. Wait for the Pico to reboot

3. Power cycle the board:

   - Unplug USB
   - Remove batteries (if any) for 10 seconds
   - Reconnect USB normally

---

## 2. Verify Firmware

Connect to Thonny and check:

```python
import sys
print(sys.implementation)
```

You should see `version=(1, 26, 0, '')` and `Raspberry Pi Pico2 W (Inky)`.

---

## 3. Resolve Module Imports

1. Ensure no old `picographics` files or directories are present in `/lib`.
2. Verify PicoGraphics is available:

```python
import picographics
print(len(dir(picographics)))  # Should print ~50
print([n for n in dir(picographics) if "INKY" in n])
```

Expected display constants:

```
['DISPLAY_INKY_FRAME',
 'DISPLAY_INKY_FRAME_4',
 'DISPLAY_INKY_FRAME_7',
 'DISPLAY_INKY_FRAME_SPECTRA_7',
 'DISPLAY_INKY_PACK']
```

---

## 4. Correct Display Constant

For the Inky Frame 7.3 Spectra (6-color):

```python
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_SPECTRA_7
from inky_frame import *

graphics = PicoGraphics(DISPLAY_INKY_FRAME_SPECTRA_7)
```

---

## 5. Minimal Test Script

```python
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_SPECTRA_7
from inky_frame import *

graphics = PicoGraphics(DISPLAY_INKY_FRAME_SPECTRA_7)

graphics.set_pen(WHITE)
graphics.clear()

graphics.set_pen(BLACK)
graphics.set_font("sans")
graphics.text("INKY FRAME OK", 40, 120, scale=3)

graphics.update()
```

- Expect a slow refresh (~10–20s)
- USB-only power works for static images
- For frequent updates or full-speed display, a 3.7 V LiPo battery is recommended

---

## 6. Notes

- Old constant names like `inky7_3_6_colour` are **no longer valid** on v1.26.1 firmware.
- Always verify the correct display constant using:

```python
import picographics
print([n for n in dir(picographics) if "INKY" in n])
```

- This ensures compatibility across firmware versions.

---

## 7. References

- [Pimoroni Inky Frame Firmware Releases](https://github.com/pimoroni/inky-frame/releases/latest)
- [Getting Started with Inky Frame](https://learn.pimoroni.com/article/getting-started-with-inky-frame)
