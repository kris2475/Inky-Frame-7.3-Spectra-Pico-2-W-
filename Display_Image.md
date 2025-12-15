# Streaming an Image to the Inky Frame 7.3" Spectra (Pico 2 W)

This guide documents the three phases required to convert an image, serve it from your PC, and stream the raw pixel data to the Inky Frame over Wi-Fi. This process assumes you have completed the steps in `setup.md` and are using the specialized Pimoroni MicroPython firmware (`pico2_w_inky-v1.26.1-micropython-without-filesystem.uf2`).

---

## Phase 1: Image Preparation (PC)

Before streaming, a standard image (JPG, PNG) must be processed into a raw binary format compatible with the display's 8-color palette.

### 1.1 Required Dependencies

Ensure you have the Pillow library installed on your PC:

```bash
pip install Pillow
```

### 1.2 Image Processing Script (`image_prep.py`)

Use the following script to load a source image, resize it to the display's resolution (800x480), quantize it to the 8-color palette using dithering, and save it as a raw binary file.

```python
# image_prep.py (Run this on your PC)
from PIL import Image

# --- Inky Frame 7.3" Spectra 8-Color Palette (RGB) ---
PALETTE = [
    (0, 0, 0),        # 0: Black
    (255, 255, 255),  # 1: White
    (0, 255, 0),      # 2: Green
    (0, 0, 255),      # 3: Blue
    (255, 0, 0),      # 4: Red
    (255, 255, 0),    # 5: Yellow
    (255, 128, 0),    # 6: Orange
    (128, 128, 128)   # 7: Taupe/Gray
]

# Expand the palette to 256 entries for Pillow
palette_expanded = PALETTE + [(0, 0, 0)] * (256 - len(PALETTE))

def prepare_image(source_path, target_path="image_data.dat", display_width=800, display_height=480):
    """
    1. Resizes the image.
    2. Quantizes the image to the 8-color Spectra palette using dithering.
    3. Saves the raw 8-bit index data to a file.
    """
    try:
        img = Image.open(source_path).convert("RGB")
        print(f"Loaded image: {source_path}")

        # 1. Resize/Crop
        img = img.resize((display_width, display_height))
        
        # 2. Quantize (Uses Floyd-Steinberg dithering for e-paper)
        pil_palette = Image.new("P", (1, 1))
        pil_palette.putpalette([c for color in palette_expanded for c in color])

        img_quantized = img.quantize(palette=pil_palette, dither=Image.Dither.FLOYDSTEINBERG)
        print("Quantized and dithered image to 8-color palette.")

        # 3. Save Raw Byte Data
        imagedata = img_quantized.tobytes()

        with open(target_path, "wb") as f:
            f.write(imagedata)

        print(f"Successfully saved {len(imagedata)} bytes of image data to {target_path}")
        print(f"The file {target_path} is ready for serving.")

    except FileNotFoundError:
        print(f"ERROR: Source file not found at {source_path}")
    except Exception as e:
        print(f"An error occurred during processing: {e}")

# Example Usage:
# Replace 'my_original_image.jpg' with your file name
# prepare_image("my_original_image.jpg")
```

### 1.3 Execution

Place your source image (e.g., `wallpaper.png`) in the same folder as `image_prep.py`.

Run the script:

```python
prepare_image("wallpaper.png")
```

Verify that a new file named `image_data.dat` has been created in the folder.

---

## Phase 2: Data Serving (PC)

The Pico W will connect to your PC's IP address and request the `image_data.dat` file.

### 2.1 Configuration

| Setting       | Value                       |
|---------------|-----------------------------|
| PC Host IP    | 192.168.0.3 (Your Wi-Fi IPv4 Address) |
| Server Port   | 8000                        |
| File          | image_data.dat              |

### 2.2 Execution

Open a terminal (PowerShell/Command Prompt) on your PC. Navigate to the folder containing `image_data.dat` and start the simple HTTP server:

```bash
python -m http.server 8000
```

- **Crucial Check:** Ensure the server terminal remains open and running. If the Pico W connects, you will see a `200 OK` log entry.  
- **Firewall:** If connections fail, ensure your Windows Firewall has an inbound rule allowing traffic on TCP Port 8000.

---

## Phase 3: Image Streaming & Display (Pico W)

This script handles Wi-Fi connection, HTTP request, and byte-by-byte drawing on the e-paper.

### 3.1 Pico W Files

Upload the following files to the root of your Pico W using Thonny:

- `boot.py`: (One line to auto-run the app)

```python
import image_display
```

- `image_display.py`: (The main application, complete script below)

### 3.2 The Final Application Script (`image_display.py`)

```python
# image_display.py (Run this on the Raspberry Pi Pico 2 W)

import time
import network
import urequests
# Import PicoGraphics and the display constant (included in your firmware)
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_SPECTRA_7

# --- Configuration ---
WIFI_SSID = "SKYYRMR7"
WIFI_PASSWORD = "K2xWvDFZkuCh"
HOST_IP = "192.168.0.3"
IMAGE_URL = f"http://{HOST_IP}:8000/image_data.dat"
# ---------------------

# --- Display Setup ---
graphics = PicoGraphics(DISPLAY_INKY_FRAME_SPECTRA_7)

# Get dimensions using the correct PicoGraphics method
WIDTH, HEIGHT = graphics.get_bounds()

# Define pens for status messages
WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)
RED = graphics.create_pen(255, 0, 0)

graphics.set_pen(WHITE)
graphics.clear()
graphics.update()

# --- Utility Functions ---

def status(message):
    """Displays a status message on the screen."""
    print(f"STATUS: {message}")
    graphics.set_pen(WHITE)
    graphics.clear()
    graphics.set_pen(BLACK)
    graphics.text(message, 10, 10, scale=3)
    graphics.update()

def network_connect(ssid, password):
    """Connects to the specified Wi-Fi network."""
    status("Connecting...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    timeout = 15
    while timeout > 0:
        if wlan.status() == network.STAT_GOT_IP:
            status(f"Connected! IP: {wlan.ifconfig()[0]}")
            time.sleep(1)
            return True
        timeout -= 1
        time.sleep(1)
    
    status("Wi-Fi Fail")
    time.sleep(5)
    return False

def fetch_and_display_image():
    """Fetches the raw image data and draws it pixel by pixel."""
    status("Fetching data...")
    
    try:
        response = urequests.get(IMAGE_URL)
        
        if response.status_code == 200:
            status("Displaying image...")
            
            # Draw raw 8-bit index data byte-by-byte
            imagedata = response.content
            x = 0
            y = 0
            
            for color_index in imagedata:
                if x >= WIDTH:
                    x = 0
                    y += 1
                
                if y < HEIGHT:
                    # The color_index (0-7) is set as the pen color
                    graphics.set_pen(color_index)
                    graphics.pixel(x, y)
                    x += 1
                else:
                    break
            
            graphics.update() # Triggers the long screen refresh
            response.close()
            return True
        
        else:
            status(f"Server Error: {response.status_code}")
            response.close()
            time.sleep(5)
            return False

    except Exception as e:
        status(f"Connection Fail: {e}")
        time.sleep(5)
        return False

# --- Main Execution ---

if network_connect(WIFI_SSID, WIFI_PASSWORD):
    fetch_and_display_image()

time.sleep(10)
```

### 3.3 Final Execution

- **Power:** Connect the Inky Frame to a reliable external USB power adapter (not your computer's USB port) to ensure enough current for the display refresh.  
- **Run:** In Thonny, click the Run button (or execute `exec(open('image_display.py').read())` in the console).  
- **Monitor:** The screen will show "Connecting...", then "Connected!", then "Fetching data...", and finally "Displaying image...".  
- **Wait:** The display will flash dark/light for 15-30 seconds. This is normal. The static image will appear when the refresh is complete.
