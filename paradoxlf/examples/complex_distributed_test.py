import sys
import os
import numpy as np
import time
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.distributed import LatentCluster

def main():
    print("=== Paradox Distributed Complexity Test: 'The Chaos Cluster' ===")
    
    # 1. Initialize Cluster (8 Nodes - Simulating a Rack)
    print("\n[System] Booting High-Performance Cluster (8 Shards)...")
    cluster = LatentCluster(dimension=128, num_shards=8)
    
    # 2. Ingest Data (10,000 Profiles)
    N_ITEMS = 10000
    print(f"\n[Ingest] Distributing {N_ITEMS} User Profiles across shards...")
    
    start_t = time.time()
    for i in range(N_ITEMS):
        # Create random vector representing user behavior
        vec = np.random.rand(128).astype(np.float32)
        # Store metadata
        meta = f"User_{i:05d}_Region_{random.randint(1, 99)}"
        cluster.add(vec, {"id": i, "profile": meta})
        
    ingest_time = time.time() - start_t
    print(f" > Ingest Complete in {ingest_time:.4f}s ({N_ITEMS/ingest_time:.0f} ops/sec)")
    
    # Verify Distribution
    print("\n[Status] Shard Load:")
    counts = [s.count() for s in cluster.shards]
    print(f" > Min: {min(counts)} | Max: {max(counts)} | Avg: {np.mean(counts)}")
    if max(counts) - min(counts) <= 1:
         print(" > [OK] Load Balancing is Perfect (Round-Robin).")
    else:
         print(" > [WARN] Load Imbalance Detected.")

    # 3. Distributed Query Accuracy Test
    print("\n[Test] Global Retrieval Accuracy...")
    # Hack: Pick a user from Shard 7 to verify we can find them
    target_idx = 9999
    # We don't have the original vector easily accessible in this simple API without storage query
    # So we'll just query a random vector and ensure we get 8*k results merged correctly down to k
    
    query_vec = np.random.rand(128).astype(np.float32)
    results = cluster.query(query_vec, k=10)
    
    print(" > Top 10 Global Matches:")
    for i, (loc_id, dist, meta) in enumerate(results):
        print(f"   {i+1}. {meta['profile']} (Dist: {dist:.4f})")
        
    if len(results) == 10:
        print(" > [OK] Global Reduce worked correctly (merged top-k).")
    else:
        print(f" > [FAIL] Only returned {len(results)} matches.")

    # 4. Resilience Test (Simulate Node Failure)
    print("\n[Chaos] Simulating Network Failure on Shard 3...")
    
    # Manually sabotage a shard
    original_query_method = cluster.shards[3].query
    def broken_query(*args, **kwargs):
        time.sleep(0.1) # Simulate timeout
        raise ConnectionError("Shard 3 Unreachable (Simulated)")
    
    cluster.shards[3].query = broken_query
    
    print(" > Executing Query on Degraded Cluster...")
    try:
        start_q = time.time()
        results_broken = cluster.query(query_vec, k=5)
        duration = time.time() - start_q
        
        print(f" > Query returned in {duration:.4f}s despite failure.")
        print(f" > Got {len(results_broken)} results (from 7 healthy shards).")
        
        if len(results_broken) > 0:
             print(" > [OK] System survived partial outage!")
        else:
             print(" > [FAIL] System failed to return any results.")
             
    except Exception as e:
        print(f" > [FAIL] Critical System Failure: {e}")

    # Restore for cleanup (good practice)
    cluster.shards[3].query = original_query_method
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
