# image_prep.py (Run this on your PC)
from PIL import Image, ImageEnhance 

# --- Inky Frame 7.3" Spectra Palette ---
# CRITICAL FIX: Removed Taupe/Gray to force mapping to more vibrant primaries.
PALETTE = [
    (0, 0, 0),        # Black (0)
    (255, 255, 255),  # White (1)
    (0, 255, 0),      # Green (2)
    (0, 0, 255),      # Blue (3)
    (255, 0, 0),      # Red (4)
    (255, 255, 0),    # Yellow (5)
    (255, 128, 0),    # Orange (6)
    # (128, 128, 128) # Taupe/Gray (7) - THIS COLOR IS NOW EXCLUDED
]

# Expand the palette to 256 entries for Pillow
palette_expanded = PALETTE + [(0, 0, 0)] * (256 - len(PALETTE))


def prepare_image(source_path, target_path="image_data.dat", preview_path="preview_quantized.png", display_width=800, display_height=480):
    """
    1. Loads, brightens, and increases contrast.
    2. Resizes and quantizes the image using a primary-only palette.
    3. Saves the raw 8-bit index data and a PNG preview for visual checking.
    """
    try:
        img = Image.open(source_path).convert("RGB")
        print(f"Loaded image: {source_path}")

        # === 1. Adjustment ===
        # Dialing back slightly from aggressive, but keeping it bright
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.4) 
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        print(f"Applied Brightness (x1.4) and Contrast (x1.2) enhancement.")
        
        # 2. Resize/Crop
        img = img.resize((display_width, display_height))
        print("Resized image.")

        # 3. Quantize (Testing with NO DITHERING for raw mapping)
        pil_palette = Image.new("P", (1, 1))
        pil_palette.putpalette([c for color in palette_expanded for c in color])

        # CRITICAL CHANGE: Dither=Image.Dither.NONE shows raw nearest-color mapping
        img_quantized = img.quantize(palette=pil_palette, dither=Image.Dither.NONE)
        print("Quantized image using a 7-color palette and NO DITHERING.")

        # 4. Save Raw Byte Data (for Pico W streaming)
        imagedata = img_quantized.tobytes()
        with open(target_path, "wb") as f:
            f.write(imagedata)
        print(f"Successfully saved {len(imagedata)} bytes of raw data to {target_path}")

        # 5. Save PNG Preview (for PC check)
        img_quantized.convert("RGB").save(preview_path)
        print(f"Successfully saved PNG preview to {preview_path}")


    except FileNotFoundError:
        print(f"Error: Source image not found at {source_path}")
    except Exception as e:
        print(f"An error occurred during image preparation: {e}")


if __name__ == '__main__':
    # ACTION: Update "source_image.jpg" to your actual image file name.
    prepare_image("source_image.jpg")
