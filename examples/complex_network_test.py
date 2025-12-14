import sys
import os
import time
import numpy as np
import threading
import uvicorn
import requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.distributed import ShardServer, RemoteShard, LatentCluster

# We need to subclass LatentCluster to accept custom shard objects (RemoteShard)
# default LatentCluster creates LatentShard (local).
# We'll monkey-patch or just clear and append.

def run_server(port, shard_id):
    server = ShardServer(dimension=64, shard_id=shard_id)
    config = uvicorn.Config(server.app, host="127.0.0.1", port=port, log_level="critical")
    server_instance = uvicorn.Server(config)
    server_instance.run()

def main():
    print("=== Paradox Complex Network Test: 'The Hybrid Cloud' ===")
    
    # 1. Spin up 3 Remote Servers (Simulating Cloud Nodes)
    ports = [8201, 8202, 8203]
    threads = []
    
    print("\n[Cloud] Booting 3 Remote Shards...")
    for i, p in enumerate(ports):
        t = threading.Thread(target=run_server, args=(p, f"cloud_node_{i}"), daemon=True)
        t.start()
        threads.append(t)
        
    time.sleep(3) # Wait for servers to settle
    
    # 2. Configure Cluster with Remote Shards
    print("\n[System] Configuring Distributed Cluster...")
    cluster = LatentCluster(dimension=64, num_shards=0) # Empty init
    
    # Manually attach RemoteShards
    for p in ports:
        remote = RemoteShard(host="127.0.0.1", port=p)
        cluster.shards.append(remote)
        
    print(f" > Cluster Online with {len(cluster.shards)} Remote Shards.")
    
    # 3. Distributed Ingest (Over Network)
    print("\n[Ingest] Uploading Data to Cloud...")
    start_t = time.time()
    for i in range(100):
        vec = np.random.rand(64).astype(np.float32)
        # Round robin happens in cluster.add
        cluster.add(vec, {"id": i, "payload": f"Data_Packet_{i}"})
        
    duration = time.time() - start_t
    print(f" > Uploaded 100 items in {duration:.4f}s")
    
    # 4. Verify Remote Counts
    total = 0
    for s in cluster.shards:
        c = s.count()
        print(f"   - {s.id}: {c} items")
        total += c
    print(f" > Total Cloud Data: {total}")
    
    if total == 100:
        print(" > [OK] Data Synchronization Complete.")
    else:
        print(" > [FAIL] Data Loss Detected.")

    # 5. Distributed Query
    print("\n[Query] Executing Cross-Node Search...")
    q_vec = np.random.rand(64).astype(np.float32)
    
    # This calls query() on all 3 remote servers in parallel threads!
    results = cluster.query(q_vec, k=5)
    
    print(" > Top 5 Results from Cloud:")
    for i, (rid, dist, meta) in enumerate(results):
        print(f"   {i+1}. {meta['payload']} (Dist: {dist:.4f})")
        
    if len(results) == 5:
        print(" > [OK] Hybrid Distributed Query Successful.")
    else:
        print(" > [FAIL] Query failed.")

    print("\n=== Test Complete ===")
    # Threads die on exit

if __name__ == "__main__":
    main()
