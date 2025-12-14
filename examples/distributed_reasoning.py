import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.distributed import LatentCluster

def main():
    print("=== Paradox Distributed Reasoning Demo (v0.16.0) ===")
    
    # 1. Setup Cluster (3 Shards)
    cluster = LatentCluster(dimension=4, num_shards=3)
    
    # 2. Distribute Knowledge
    # We use simple 4D vectors for logical clarity
    # Concept: King  = [1, 1, 1, 0]
    # Concept: Man   = [0, 1, 0, 0]
    # Concept: Woman = [0, 1, 0, 1]
    # Concept: Queen = [1, 1, 1, 1] (Target)
    
    vec_king  = np.array([1, 1, 1, 0], dtype=np.float32)
    vec_man   = np.array([0, 1, 0, 0], dtype=np.float32)
    vec_woman = np.array([0, 1, 0, 1], dtype=np.float32)
    vec_queen = np.array([1, 1, 1, 1], dtype=np.float32)
    
    # Shard 0 knows King
    cluster.shards[0].add(vec_king, {"name": "King"})
    print("[Shard 0] Learned 'King'")
    
    # Shard 1 knows Man & Woman
    cluster.shards[1].add(vec_man, {"name": "Man"})
    cluster.shards[1].add(vec_woman, {"name": "Woman"})
    print("[Shard 1] Learned 'Man' and 'Woman'")
    
    # Shard 2 knows Queen
    cluster.shards[2].add(vec_queen, {"name": "Queen"})
    print("[Shard 2] Learned 'Queen'")
    
    # 3. Perform Distributed Reasoning
    print("\n[Reasoning] Solving: King - Man + Woman = ???")
    
    # The cluster itself calculates the vector: [1,1,1,0] - [0,1,0,0] + [0,1,0,1] = [1,1,1,1]
    # Then it searches ALL shards for [1,1,1,1]
    
    results = cluster.solve_analogy_distributed(vec_king, vec_man, vec_woman, k=1)
    
    print("\n[Result] Global Search Result:")
    for idx, dist, meta in results:
        print(f" > Found: {meta['name']} (Dist: {dist:.4f})")
        
    match = results[0][2]['name']
    if match == "Queen":
        print("\n[Success] Distributed Logic confirmed.")
    else:
         print(f"\n[Fail] Found {match} instead of Queen")

if __name__ == "__main__":
    main()
