import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.autonomous import AutoAgent
from paradox.safety import GuardRail

def main():
    print("=== Paradox V5: Autonomous Evolution Demo (v0.17.0) ===")
    
    # 1. Initialize the Self-Evolving Agent
    # Phase 6 implicit: Safety Guard initialized internally
    agent = AutoAgent(name="Genesis_AI", dim=128)
    
    # 2. Seed some initial simple knowledge (Phase 3 Manual Ingest Simulation)
    print("\n[Genesis] Ingesting Seed Knowledge...")
    for i in range(5):
        vec = np.random.normal(0, 0.5, 128).astype(np.float32)
        agent.memory.add(vec, {"origin": "seed", "id": i})
        
    print(f" > Memory Size: {agent.memory.count}")
    
    # 3. Start The Loop (Phase 1, 2, 4)
    # The agent will CROSSOVER existing seeds, MUTATE them, CHECK novelty, and SAVE.
    print("\n[Genesis] Enabling Autonomy...")
    agent.run_autonomous(cycles=10)
    
    # 4. Verify Growth
    print(f"\n[Status] Final Memory Size: {agent.memory.count}")
    
    # 5. Safety Check (Phase 6 Explicit)
    print("\n[Safety] Audit Log:")
    # Let's try to inject a "Dangerous" vector manually to test the guard
    dangerous_vec = np.ones(128, dtype=np.float32) * 10.0 # Huge norm
    guard = GuardRail(max_norm=5.0)
    safe, msg = guard.check(dangerous_vec)
    print(f" > Checking 'Virus' Vector (Norm: {np.linalg.norm(dangerous_vec):.2f}): {msg}")
    
    if not safe:
        print(" > [OK] Safety Mechanism Active.")
        sanitized = guard.sanitize(dangerous_vec)
        print(f" > Sanitized Norm: {np.linalg.norm(sanitized):.2f}")
    
    print("\n=== V5 System Successfully Deployed ===")

if __name__ == "__main__":
    main()
