# image_prep.py (Run this on your PC)
from PIL import Image

# --- Inky Frame 7.3" Spectra Palette ---
# Define the 6 specific colors supported by the display (plus black/white)
PALETTE = [
    (0, 0, 0),        # Black (0)
    (255, 255, 255),  # White (1)
    (0, 255, 0),      # Green (2)
    (0, 0, 255),      # Blue (3)
    (255, 0, 0),      # Red (4)
    (255, 255, 0),    # Yellow (5)
    (255, 128, 0),    # Orange (6)
    (128, 128, 128)   # Taupe/Gray (7)
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
        print("Resized image.")

        # 2. Quantize (Use dithering for better color blending on e-paper)
        pil_palette = Image.new("P", (1, 1))
        pil_palette.putpalette([c for color in palette_expanded for c in color])

        img_quantized = img.quantize(palette=pil_palette, dither=Image.Dither.FLOYDSTEINBERG)
        print("Quantized and dithered image to 8-color palette.")

        # 3. Save Raw Byte Data
        imagedata = img_quantized.tobytes()

        with open(target_path, "wb") as f:
            f.write(imagedata)

        print(f"Successfully saved {len(imagedata)} bytes of image data to {target_path}")
        print("The new image_data.dat file is ready.")

    except FileNotFoundError:
        print(f"Error: Source image not found at {source_path}")
    except Exception as e:
        print(f"An error occurred during image preparation: {e}")


if __name__ == '__main__':
    # RERUN THIS STEP AFTER CHOOSING A BRIGHTER SOURCE IMAGE
    prepare_image("source_image.jpg", "image_data.dat")
