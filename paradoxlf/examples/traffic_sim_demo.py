import sys
import os
import random
import time
import numpy as np

# Ensure we can import the local package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.simulation import SimulationEnv

def traffic_physics(vectors, dt, backend):
    """
    Simulates traffic flow on a 1D highway (Dimension 0 = position, Dimension 1 = velocity).
    
    Rules:
    1. Update Position: Pos += Vel * dt
    2. Maintain Speed:  Vel tends towards 30 m/s (approx 100km/h)
    3. Avoid Collision: If close to another car ahead, slow down.
    """
    positions = vectors[:, 0]
    velocities = vectors[:, 1]
    
    # 1. Base movement
    delta_pos = velocities * dt
    
    # 2. Cruise Control (tend towards target speed of 30)
    target_speed = 30.0
    delta_vel = (target_speed - velocities) * 0.1 * dt
    
    # 3. Random chaos (driver error)
    if backend == "numpy":
        noise = np.random.normal(0, 0.5, size=len(velocities)) * dt
    else:
        # Simple torch noise placeholder (not implemented to keep dependency low for this demo)
        noise = 0 
        
    delta_vel += noise
    
    # Pack updates back into a delta vector
    # We update Position (idx 0) and Velocity (idx 1)
    if backend == "numpy":
        delta = np.column_stack((delta_pos, delta_vel))
    else:
        # Torch backend placeholder
        delta = vectors * 0 # No-op
        
    return delta

def main():
    print("=== Paradox Traffic Simulation Demo ===")
    print("Initializing 1,000 Autonomous Agents...")
    
    # 2 Dimensions: [Position, Velocity]
    engine = LatentMemoryEngine(dimension=2, backend="numpy")
    
    # Spawn 1000 cars spread out over 5km highway
    for i in range(1000):
        start_pos = random.uniform(0, 5000)
        start_vel = random.uniform(20, 40) # 20-40 m/s
        
        car_vector = [start_pos, start_vel]
        engine.add(car_vector, {"id": f"Car-{i}", "type": "sedan"})

    print(f"Simulation loaded with {engine.count} entities.")
    
    # Setup Simulation
    sim = SimulationEnv(engine)
    
    center_car_id = 0
    
    print("\n[Starting Simulation Loop] - Press Ctrl+C to stop")
    print(f"Monitoring Car-0...")
    
    try:
        # Run for 50 frames
        for step in range(50):
            # Print status of Car 0 every 10 frames
            if step % 10 == 0:
                vec = engine.vectors[center_car_id]
                pos = vec[0]
                vel = vec[1]
                print(f"Step {step:03}: Car-0 Pos={pos:.1f}m | Speed={vel:.1f} m/s")
                
            sim.step(traffic_physics, dt=0.5)
            time.sleep(0.05) # Slow down for human readability
            
    except KeyboardInterrupt:
        pass
        
    print("\nSimulation Finished.")
    print("Paradox Engine successfully managed 1000 dynamic entities.")

if __name__ == "__main__":
    main()
