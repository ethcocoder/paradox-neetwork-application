import sys
import os
import time
from PIL import Image, ImageDraw

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.media.video import SimpleVideoEncoder, SimpleVideoDecoder, latent_interpolate

def create_frame(position_x):
    """Creates a frame with a ball at position X."""
    # White background
    img = Image.new('RGB', (64, 64), color='white')
    draw = ImageDraw.Draw(img)
    # Draw huge blue ball
    r = 10
    draw.ellipse((position_x-r, 32-r, position_x+r, 32+r), fill='blue')
    return img

def main():
    print("=== Paradox Multimedia Demo: Video Dreaming ===")
    
    width, height = 64, 64
    encoder = SimpleVideoEncoder(width, height)
    decoder = SimpleVideoDecoder(width, height)
    
    # 1. Create Keyframes (Start and End)
    # Frame A: Ball on Left (x=10)
    # Frame B: Ball on Right (x=54)
    frame_a = create_frame(10)
    frame_b = create_frame(54)
    
    print("Generated Keyframes: Start(Left) -> End(Right)")
    
    # 2. Encode to Latent Space
    vec_a = encoder.encode([frame_a])[0]
    vec_b = encoder.encode([frame_b])[0]
    
    print("Encoded to Latent Vectors.")
    
    # 3. Dream the 'Video' (Interpolate)
    # We ask the engine to generate 10 frames connecting these two states
    print("Dreaming 10 intermediate frames via Latent Interpolation...")
    latent_video = latent_interpolate(vec_a, vec_b, steps=10)
    
    # 4. Decode
    dreamed_frames = decoder.decode(latent_video)
    
    # 5. Visualize (ASCII Animation) & Save GIF
    print("\n[Playing Dreamed Video]")
    
    # Save as GIF
    gif_path = "dream_video.gif"
    dreamed_frames[0].save(
        gif_path,
        save_all=True,
        append_images=dreamed_frames[1:],
        optimize=False,
        duration=100,
        loop=0
    )
    print(f"Saved actual video to: {os.path.abspath(gif_path)}")

    for i, frame in enumerate(dreamed_frames):
        # Convert to tiny ASCII for terminal
        tiny = frame.resize((32, 16)).convert('L')
        # Simple ASCII art logic
        ascii_frame = "\n".join(["".join(["#" if tiny.getpixel((x, y)) > 50 else "." for x in range(32)]) for y in range(16)])
        
        print(f"\n--- Frame {i+1}/10 ---")
        print(ascii_frame)
        time.sleep(0.1)

    print("\nParadox successfully generated video from just 2 data points.")

if __name__ == "__main__":
    main()
