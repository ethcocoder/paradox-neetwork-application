import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.media.temporal import LatentTrajectory

def main():
    print("=== Paradox Temporal Intelligence Demo ===")
    
    # 1. Simulate a Thinking Process (Trajectory)
    # Moving from Concept A (0,0) to Concept B (10,10) in a curve
    t = np.linspace(0, 10, 10)
    x = t
    y = t + np.sin(t) # Wobbly path
    
    path = np.column_stack((x, y))
    print(f"Path Shape: {path.shape}")
    
    # 2. Analyze Trajectory
    traj = LatentTrajectory(path)
    
    avg_speed = np.mean(traj.speed())
    curvature = traj.curvature()
    
    print(f"Average Speed: {avg_speed:.4f}")
    print(f"Path Curvature: {curvature:.4f} radians (Higher = More erratic)")
    
    # 3. Predict Future
    future_linear = traj.predict_next(steps=3, method="linear")
    future_avg = traj.predict_next(steps=3, method="average")
    
    print(f"Current Pos: {path[-1]}")
    print(f"Prediction (Linear): {future_linear[-1]}")
    print(f"Prediction (Average): {future_avg[-1]}")
    
    # 4. Visualization (Optional)
    try:
        plt.figure(figsize=(8, 6))
        plt.plot(path[:,0], path[:,1], 'bo-', label='Past History')
        plt.plot(future_linear[:,0], future_linear[:,1], 'r*--', label='Prediction (Linear)')
        plt.plot(future_avg[:,0], future_avg[:,1], 'g*--', label='Prediction (Avg)')
        plt.title(f"Latent Trajectory Analysis\nSpeed: {avg_speed:.2f} | Curvature: {curvature:.2f}")
        plt.legend()
        plt.grid(True)
        
        output_file = "temporal_prediction.png"
        plt.savefig(output_file)
        print(f"\nSaved visualization to: {output_file}")
    except ImportError:
        print("Matplotlib not installed, skipping plot.")

if __name__ == "__main__":
    main()
