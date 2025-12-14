import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.distributed import LatentConsensus

def main():
    print("=== Paradox Collective Intelligence Demo (v0.15.0) ===")
    
    # Scene: 3 Agents observing the "Sky".
    # Agent A (Human): Sees Blue
    # Agent B (Camera): Sees Blueish-Grey (Cloudy)
    # Agent C (Malfunctioning Sensor): Sees Red (Error/Outlier)
    
    # 1. Define Opinions (Vectors)
    # Let's say [1, 0, 0] is Perfect Blue
    vec_perfect_blue = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    
    # Agent A: Very close to blue
    vec_a = vec_perfect_blue + np.random.normal(0, 0.05, 3) 
    
    # Agent B: Blue but dull
    vec_b = np.array([0.8, 0.2, 0.1], dtype=np.float32)
    
    # Agent C: Random Red noise (Outlier)
    vec_c = np.array([0.0, 1.0, 0.0], dtype=np.float32) 
    
    opinions = [vec_a, vec_b, vec_c]
    names = ["Agent A (Human)", "Agent B (Camera)", "Agent C (Broken)"]
    
    print("\n[Input] Opinions on 'The Sky':")
    for n, v in zip(names, opinions):
        print(f" - {n}: {v}")

    # 2. Naive Consensus (Average)
    consensus_naive = LatentConsensus.average_consensus(opinions)
    print(f"\n[Consensus] Naive Average: {consensus_naive}")
    # The red outlier will corrupt the blue sky definition
    
    # 3. Intelligent Consensus (Outlier Rejection)
    print("\n[Consensus] Applying Collaborative Filtering...")
    refined_truth, outliers = LatentConsensus.detect_outliers(opinions, threshold=0.5)
    
    print(f" > Discarded {len(outliers)} outliers.")
    for idx in outliers:
        print(f"   ! Ignored {names[idx]} (Too divergent)")
        
    print(f" > Refined Truth Vector: {refined_truth}")
    
    # Check simple semantic distance
    dist_to_truth = np.linalg.norm(refined_truth - vec_perfect_blue)
    print(f" > Distance to Absolute Truth: {dist_to_truth:.4f}")
    
    if 2 in outliers: # Index 2 is Agent C
        print("\n[Success] The Collective successfully ignored the hallucinating agent.")
    else:
        print("\n[Fail] The Collective was tricked by the broken agent.")

if __name__ == "__main__":
    main()
