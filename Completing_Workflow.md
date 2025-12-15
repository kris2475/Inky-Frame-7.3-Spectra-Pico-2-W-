# Completing the Inky Frame 7.3" Spectra Pico 2 W Workflow

This document provides instructions for setting up the PC HTTP server, managing Wi-Fi credentials, and troubleshooting, completing the workflow for streaming images to the Inky Frame 7.3" Spectra using Pico 2 W.

---

## 1. HTTP Server Setup (PC)

Before the Pico can fetch the image, you need to serve the `image_data.dat` file from your PC.

### Steps

1. Place the `image_data.dat` file in a dedicated folder, e.g., `InkyFrameImages`.
2. Open a terminal (Command Prompt or PowerShell) and navigate to that folder:

```bash
cd path_to/InkyFrameImages
```

3. Start a simple HTTP server using Python 3:

```bash
python -m http.server 8000
```

4. Keep the terminal open; this will serve the folder at:

```
http://<your_PC_IP>:8000/
```

5. Confirm that the server is accessible by opening a browser on another device and navigating to:

```
http://<your_PC_IP>:8000/image_data.dat
```

### Notes

- Make sure your Windows Firewall or any other firewall allows inbound connections on port 8000.
- The IP address (`<your_PC_IP>`) must be the IPv4 address of the PC on the same Wi-Fi network as the Pico W.

---

## 2. Wi-Fi Credentials Management

It is recommended to manage Wi-Fi credentials in a separate file for security and easier configuration.

### `secrets.py` Example

Create a file named `secrets.py` in the root of the Pico W filesystem:

```python
# secrets.py

SSID = "Your_WiFi_SSID"
PASSWORD = "Your_WiFi_Password"
```

### Usage in `image_display.py`

Replace hardcoded Wi-Fi credentials with imports from `secrets.py`:

```python
from secrets import SSID, PASSWORD

if network_connect(SSID, PASSWORD):
    fetch_and_display_image()
```

### Notes

- Keep `secrets.py` out of version control if sharing the repository publicly.
- Ensure SSID and password are correct and that the Pico W is in range of the network.

---

## 3. Troubleshooting Guide

### Wi-Fi Connection Issues

- **Symptom:** `Wi-Fi Fail` status appears.
- **Solution:**
  - Verify the SSID and password.
  - Confirm the Pico is within Wi-Fi range.
  - Restart Pico and retry.
  - Check for network restrictions (some enterprise networks block devices).

### HTTP Server Issues

- **Symptom:** Pico cannot fetch `image_data.dat`.
- **Solution:**
  - Ensure the server terminal is running.
  - Confirm the PC IP address is correct.
  - Check firewall settings to allow TCP port 8000.
  - Test the URL from another device in the same network.

### Display Refresh Issues

- **Symptom:** Screen flashes but image does not appear.
- **Solution:**
  - Ensure sufficient USB power (use a wall adapter, not computer USB port).
  - Confirm the `image_data.dat` resolution matches the display (800x480).
  - Check `image_display.py` for any errors during execution.

### General Debugging Tips

- Use print statements in `image_display.py` for step-by-step feedback.
- Verify that `PicoGraphics` and `DISPLAY_INKY_FRAME_SPECTRA_7` are correctly imported from the firmware.
- Ensure the Pico W firmware is the Pimoroni MicroPython variant (`pico2_w_inky-v1.26.1-micropython-without-filesystem.uf2`).

---

## 4. Recommended Repository Structure

```
InkyFrameProject/
│
├── image_prep.py         # PC image preprocessing script
├── image_data.dat        # Raw image data (generated)
├── secrets.py            # Wi-Fi credentials
├── boot.py               # Pico entry point
├── image_display.py      # Main Pico app
└── README.md             # Instructions and documentation
```

This structure ensures clarity and ease of use for users replicating the project.
