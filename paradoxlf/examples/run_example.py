import sys
import os
import random
import time

# Ensure we can import the local package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.simulation import SimulationEnv, simple_gravity_well

def main():
    print("=== Paradox Engine Demo ===")
    
    # 1. Initialize Engine (Auto-detects CPU/GPU)
    engine = LatentMemoryEngine(dimension=3) # 3D for easy conceptualization
    
    info = engine.get_info()
    print(f"Backend set to: {info['backend']}")
    
    # 2. Generate Example Objects
    print("\n[Generating Data...]")
    names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    for i in range(20):
        # random 3d vector
        vec = [random.uniform(-10, 10) for _ in range(3)]
        name = f"{random.choice(names)}-{i}"
        
        # Metadata
        attrs = {"name": name, "class": "entity"}
        
        # Store
        eid = engine.add(vec, attrs)
        if i < 5:
            print(f"Added {name} ID:{eid} at {vec}")
            
    print(f"Total objects: {engine.count}")

    # 3. Query
    print("\n[Testing Query...]")
    # Search near origin
    target = [0, 0, 0]
    results = engine.query(target, k=3)
    
    print(f"Nearest to {target}:")
    for rid, dist, meta in results:
        print(f" - ID: {rid} | Name: {meta['name']} | Dist: {dist:.4f}")

    # 4. Simulation
    print("\n[Running Simulation - 'Gravity Well'...]")
    sim = SimulationEnv(engine)
    
    def monitor(step, eng):
        if step % 5 == 0:
            # Check ID 0's position to see if it's moving
            vec0 = eng.vectors[0]
            print(f"Step {step}: Obj-0 Pos: {vec0}")

    sim.run(steps=20, dynamics_fn=simple_gravity_well, dt=0.5, callback=monitor)
    
    print("\n[Post-Sim Query...]")
    # Should be closer to origin now
    results = engine.query(target, k=3)
    for rid, dist, meta in results:
        print(f" - ID: {rid} | Name: {meta['name']} | Dist: {dist:.4f}")

if __name__ == "__main__":
    main()
