# image_display.py (Run this on the Raspberry Pi Pico 2 W)

import time
import network
import machine
import sys
from micropython import const
import urequests

# CRITICAL FIX: Use PicoGraphics directly, which is always available 
# in the specialized Pimoroni firmware.
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_SPECTRA_7 

# --- Configuration (Your FINAL details are inserted) ---
WIFI_SSID = "SKYYRMR7"
WIFI_PASSWORD = "K2xWvDFZkuCh"
HOST_IP = "192.168.0.3" 
# CORRECTED FILE NAME: image_data.dat
IMAGE_URL = f"http://{HOST_IP}:8000/image_data.dat"
UPDATE_INTERVAL = 3600 # Update every hour (in seconds)
# ----------------------------------------------------------------------

# --- Global Display Setup (Matches your hardware and firmware) ---

# Initialize the display using PicoGraphics directly
# We must pass the correct display constant for your 7.3" Spectra screen
graphics = PicoGraphics(DISPLAY_INKY_FRAME_SPECTRA_7)

# === CRITICAL FIX: Get bounds using the correct method ===
WIDTH, HEIGHT = graphics.get_bounds() # Correct way to get dimensions
# =========================================================

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
    """Fetches the image data and displays it on the screen."""
    status("Fetching data...")
    
    try:
        response = urequests.get(IMAGE_URL)
        
        if response.status_code == 200:
            status("Displaying image...")
            
            # The data is raw 8-bit index data: 1 byte per pixel.
            imagedata = response.content
            x = 0
            y = 0
            
            for color_index in imagedata:
                if x >= WIDTH:
                    x = 0
                    y += 1
                
                if y < HEIGHT:
                    # Color index (0-7) corresponds to the 8-color palette
                    graphics.set_pen(color_index)
                    graphics.pixel(x, y)
                    x += 1
                else:
                    break
            
            graphics.update()
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
# To save power, you would typically call graphics.sleep() here.
