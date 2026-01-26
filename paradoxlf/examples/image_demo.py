import sys
import os
import random
from PIL import Image, ImageDraw

# Ensure local import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.media.image import SimpleImageEncoder, SimpleImageDecoder

def generate_dummy_image(color, shape="circle"):
    """Creates a simple PIL image for testing."""
    img = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    if shape == "circle":
        draw.ellipse((25, 25, 75, 75), fill=color)
    else:
        draw.rectangle((25, 25, 75, 75), fill=color)
        
    return img

def main():
    print("=== Paradox Multimedia Demo: Image Search ===")
    
    # 1. Setup Engine with Image capability
    # We use 32x32 images for speed -> 32*32*3 = 3072 dimensions
    img_size = 32
    encoder = SimpleImageEncoder(width=img_size, height=img_size)
    decoder = SimpleImageDecoder(width=img_size, height=img_size)
    
    engine = LatentMemoryEngine(dimension=encoder.dimension)
    engine.set_encoder(encoder)
    engine.set_decoder(decoder)
    
    # 2. Add Data (Generated Red, Green, Blue images)
    colors = ["red", "green", "blue", "orange", "purple"]
    shapes = ["circle", "square"]
    
    print("\n[Indexing Images...]")
    for color in colors:
        for shape in shapes:
            name = f"{color}_{shape}"
            img = generate_dummy_image(color, shape)
            
            # Paradox automatically encodes the image to a vector here!
            eid = engine.add(img, {"name": name}) 
            print(f" - Indexed: {name}")

    # 3. Search
    print("\n[Searching...]")
    # We want to find something similar to a "Red Square"
    query_img = generate_dummy_image("red", "square")
    # Add slight noise/difference to make it interesting? (Not done here for simplicity)
    
    # We encode the query image manually to get the vector for search
    query_vec = encoder.encode(query_img)
    
    results = engine.query(query_vec, k=3, metric="cosine")
    
    print(f"Top matches for 'Red Square':")
    for rid, dist, meta in results:
        # Distance (1 - sim) should be close to 0 for exact match
        print(f" - {meta['name']} (Score: {1-dist:.4f})")
        
    # 4. Reconstruction
    print("\n[Reconstructing Memory from Latent Space...]")
    # Let's pull the vector for the first result and turn it back into an image
    best_match_id = results[0][0]
    best_vec = engine.vectors[best_match_id]
    
    recon_img = decoder.decode(best_vec)
    recon_img.save("reconstructed_image.png")
    print(f"Successfully reconstructed ID {best_match_id} ({engine.retrieve(best_match_id)['name']})")
    print(f"Saved reconstruction to: {os.path.abspath('reconstructed_image.png')}")
    print("Multimedia Pipeline Verified.")

if __name__ == "__main__":
    main()
