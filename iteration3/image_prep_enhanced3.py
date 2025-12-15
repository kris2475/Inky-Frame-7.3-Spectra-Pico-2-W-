# image_prep.py (Run this on your PC)
from PIL import Image, ImageEnhance 

# --- Inky Frame 7.3" Spectra Palette (Optimized 7 Colors) ---
# We keep the Taupe/Gray (128, 128, 128) EXCLUDED to prevent it from dominating.
PALETTE = [
    (0, 0, 0),        # Black (0)
    (255, 255, 255),  # White (1)
    (0, 255, 0),      # Green (2)
    (0, 0, 255),      # Blue (3)
    (255, 0, 0),      # Red (4)
    (255, 255, 0),    # Yellow (5)
    (255, 128, 0),    # Orange (6)
]

# Expand the palette to 256 entries for Pillow
palette_expanded = PALETTE + [(0, 0, 0)] * (256 - len(PALETTE))


def prepare_image(source_path, target_path="image_data.dat", preview_path="preview_quantized.png", display_width=800, display_height=480):
    """
    1. Loads, brightens, and increases contrast optimally.
    2. Resizes and quantizes using the optimized 7-color palette and Floyd-Steinberg dithering.
    3. Saves the raw 8-bit index data and a PNG preview.
    """
    try:
        img = Image.open(source_path).convert("RGB")
        print(f"Loaded image: {source_path}")

        # === 1. Optimal Enhancement ===
        # Brightness 1.4: Ensures the image is clearly visible.
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.4) 
        # Contrast 1.2: Provides separation between colors without being too harsh.
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        print(f"Applied Optimal Brightness (x1.4) and Contrast (x1.2) enhancement.")
        
        # 2. Resize/Crop
        img = img.resize((display_width, display_height))
        print("Resized image.")

        # 3. Quantize (Re-enabling Floyd-Steinberg Dithering)
        pil_palette = Image.new("P", (1, 1))
        pil_palette.putpalette([c for color in palette_expanded for c in color])

        # CRITICAL CHANGE: Dither=Image.Dither.FLOYDSTEINBERG
        img_quantized = img.quantize(palette=pil_palette, dither=Image.Dither.FLOYDSTEINBERG)
        print("Quantized image using 7-color palette and FLOYD-STEINBERG DITHERING.")

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
