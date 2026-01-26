import sys
import os
import numpy as np
from PIL import Image

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.media.image import SimpleImageEncoder, SimpleImageDecoder
from paradox.media.temporal import LatentTrajectory

def create_gradient_frame(step, total_steps):
    """
    Generates an image that transitions from RED to BLUE.
    Step 0 = Red (255, 0, 0)
    Step N = Blue (0, 0, 255)
    """
    ratio = step / (total_steps - 1)
    r = int(255 * (1 - ratio))
    g = 0
    b = int(255 * ratio)
    
    # Create 64x64 image of this color
    img = Image.new('RGB', (64, 64), (r, g, b))
    return img

def main():
    print("=== Paradox Complex Temporal Prediction Test ===")
    print("Scenario: Observing a color shifting from Red to Blue.")
    print("Goal: Predict the 'Future' color after the sequence ends.\n")
    
    # 1. Setup Engine & Encoders
    # We use SimpleEncoder because we want to DECODE the result to see it.
    # CLIP cannot decode.
    encoder = SimpleImageEncoder(width=64, height=64)
    decoder = SimpleImageDecoder(width=64, height=64)
    
    # 2. Generate "Video" Sequence (10 Frames)
    frames = []
    vectors = []
    
    print("Generating Observation Sequence (10 Frames)...")
    for i in range(10):
        img = create_gradient_frame(i, 10)
        vec = encoder.encode(img)
        frames.append(img)
        vectors.append(vec)
        print(f" Frame {i}: Color ~ R={255*(1-i/9):.0f} B={255*(i/9):.0f}")

    # 3. Analyze Trajectory
    print("\nAnalyzing Latent Trajectory...")
    traj = LatentTrajectory(vectors)
    
    speed = np.mean(traj.speed())
    print(f"Transformation Speed: {speed:.4f} units/frame")
    
    # 4. Predict Future
    print("Predicting Next 3 Steps (Extrapolating Trend)...")
    # We use linear prediction to follow the momentum (Red -> Blue -> Ultra Blue?)
    future_vecs = traj.predict_next(steps=3, method="linear")
    
    # 5. Visualize the Future
    print("\nReconstructing Predicted Future...")
    for i, pred_vec in enumerate(future_vecs):
        # Decode the predicted latent vector back to pixels
        future_img = decoder.decode(pred_vec)
        
        fname = f"prediction_step_{i+1}.png"
        future_img.save(fname)
        
        # Analyze the color of the reconstruction
        # (Simple average of center pixel)
        center_pixel = future_img.getpixel((32, 32))
        print(f" Future +{i+1}: Saved to {fname} | Color: {center_pixel}")
        
    print("\nAnalysis:")
    print("If successful, Future +1 should be Pure Blue or slightly beyond (clamped).")
    print("This proves Paradox can model and extrapolate visual processes.")

if __name__ == "__main__":
    main()
