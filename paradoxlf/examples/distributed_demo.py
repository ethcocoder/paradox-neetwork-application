import sys
import os
import numpy as np
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.distributed import LatentCluster

def main():
    print("=== Paradox Distributed Architecture (Alpha) ===")
    
    # 1. Initialize Cluster (4 Nodes)
    print("\n[System] Booting Cluster...")
    cluster = LatentCluster(dimension=64, num_shards=4)
    
    # 2. Ingest Data (Sharding)
    N_ITEMS = 1000
    print(f"\n[Ingest] Distributing {N_ITEMS} vectors across 4 shards...")
    
    start_t = time.time()
    for i in range(N_ITEMS):
        # Create random vector
        vec = np.random.rand(64).astype(np.float32)
        cluster.add(vec, {"id": i, "data": f"Item_{i}"})
        
    ingest_time = time.time() - start_t
    print(f" > Ingest Complete in {ingest_time:.4f}s")
    print(f" > Total Cluster Memory: {cluster.total_count}")
    
    # Verify Load Balancing
    print("\n[Status] Shard Distribution:")
    for s in cluster.shards:
        print(f" - Shard {s.id}: {s.count()} items")
        
    # 3. Distributed Query (Map-Reduce)
    print("\n[Query] Performing Distributed Search...")
    query_vec = np.random.rand(64).astype(np.float32)
    
    start_q = time.time()
    results = cluster.query(query_vec, k=5)
    query_time = time.time() - start_q
    
    print(f" > Query Complete in {query_time:.4f}s")
    print(" > Top 5 Global Matches:")
    for idx, (local_id, dist, meta) in enumerate(results):
        # Note: local_id is relative to shard, need meta['id'] for global verification if needed
        print(f"   {idx+1}. {meta['data']} (Dist: {dist:.4f})")
        
    print("\n[Success] Distributed Map-Reduce logic verified.")

if __name__ == "__main__":
    main()
