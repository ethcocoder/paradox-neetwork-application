import sys
import os
from PIL import Image, ImageDraw
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.media.image import SimpleImageEncoder, SimpleImageDecoder
from paradox.mixer import ParadoxMixer

def create_color_img(color):
    img = Image.new('RGB', (64, 64), color=color)
    return img

def main():
    print("=== Paradox Phase 3: Latent Blending Demo ===")
    
    # Setup
    encoder = SimpleImageEncoder(64, 64)
    decoder = SimpleImageDecoder(64, 64)
    mixer = ParadoxMixer()
    
    # 1. Create Base Concepts (Images)
    print("Creating Base Concepts: Red & Blue")
    img_red = create_color_img('red')
    img_blue = create_color_img('blue')
    
    # 2. Encode to Vector Space
    vec_red = encoder.encode(img_red)
    vec_blue = encoder.encode(img_blue)
    
    # 3. Blend Concepts (50% Red + 50% Blue should contain Purple data)
    print("Blending: 50% Red + 50% Blue...")
    vec_purple = mixer.interpolate(vec_red, vec_blue, ratio=0.5)
    
    # 4. Decode Result
    img_purple = decoder.decode(vec_purple)
    
    # 5. Verify & Save
    outfile = "blended_purple.png"
    img_purple.save(outfile)
    print(f"Blended image saved to: {outfile}")
    
    # Check pixel value of center pixel
    center_pixel = img_purple.getpixel((32, 32))
    print(f"Center Pixel RGB: {center_pixel}")
    # Red is (255, 0, 0), Blue is (0, 0, 255) -> Purple approx (127, 0, 127)
    
    if center_pixel[0] > 100 and center_pixel[2] > 100:
        print("SUCCESS: The result is Purple!")
    else:
        print("WARNING: Blending might have failed.")

if __name__ == "__main__":
    main()
