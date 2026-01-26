import sys
import os
import shutil
import time
import threading
import numpy as np
import requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.distributed import ShardServer, RemoteShard

PERSISTENCE_FILE = "./data/test_shard.pkl"

def run_server_for_some_time(port, duration_sec):
    # Start server with persistence enabled
    server = ShardServer(dimension=64, shard_id="cloud_node_test", persistence_path=PERSISTENCE_FILE)
    
    # We need to run it in a way we can stop it to simulate "Crash"
    # Uvicorn doesn't have a clean stop in threaded mode easily without separate process
    # So we'll trust the persistence logic triggers on 'add' or manual save.
    
    # For test, we will expose the server instance globally to the thread so we can call methods
    import uvicorn
    config = uvicorn.Config(server.app, host="127.0.0.1", port=port, log_level="critical")
    server_instance = uvicorn.Server(config)
    
    # We run in a separate thread
    t = threading.Thread(target=server_instance.run, daemon=True)
    t.start()
    return server, server_instance

def main():
    print("=== Paradox Cloud Persistence Test ===")
    
    # Cleanup previous run
    if os.path.exists("./data"):
        shutil.rmtree("./data")
    
    # 1. Start "Node A" (Fresh)
    print("\n[Phase 1] Booting Node A (Fresh)...")
    port = 8300
    server_ref, uvi_ref = run_server_for_some_time(port, 0)
    time.sleep(2) # Boot wait
    
    # 2. Add Data to Node A
    print("[Phase 1] Ingesting Critical Data...")
    client = RemoteShard(host="127.0.0.1", port=port)
    
    vec = np.random.rand(64).astype(np.float32)
    client.add(vec, {"mission": "Save the World"})
    print(" > Data Added: 'Save the World'")
    
    # Force a save (User logic: saves every 10 items, or we can assume it didn't save yet)
    # Let's add 9 more items to trigger auto-save (mod 10)
    for i in range(9):
        client.add(np.random.rand(64).astype(np.float32), {"filler": i})
        
    print(" > trigger auto-save (10 items total).")
    time.sleep(1) # Wait for IO
    
    # 3. Simulate CRASH (Stop Node A)
    print("\n[Phase 2] Simulating CLOUD INSTANCE CRASH...")
    # In threaded uvicorn, 'forcing' a stop is hard aka we just ignore it and start a NEW server on NEW port checking file
    # But to prove persistence, we just need to verify the FILE exists.
    
    if os.path.exists(PERSISTENCE_FILE):
        print(f" > [OK] Snapshot file found at {PERSISTENCE_FILE}")
        size = os.path.getsize(PERSISTENCE_FILE)
        print(f" > Snapshot Size: {size} bytes")
    else:
        print(" > [FAIL] Snapshot file NOT found!")
        return

    # 4. Restart as "Node B" (Recovery) using same file
    print("\n[Phase 3] Booting Node B (Recovery Mode)...")
    # We can't reuse port 8300 easily if old thread holds it. Use 8301.
    port_b = 8301
    server_ref_b, uvi_ref_b = run_server_for_some_time(port_b, 0)
    time.sleep(2)
    
    # 5. Verify Memory
    print("[Phase 3] checking Memory integrity...")
    client_b = RemoteShard(host="127.0.0.1", port=port_b)
    
    count = client_b.count()
    print(f" > Restored Memory Count: {count}")
    
    if count == 10:
        print(" > [OK] Full Recovery Successful!")
    else:
        print(f" > [FAIL] Expected 10 items, got {count}")
        
    # Query to be sure content is correct
    print(" > Querying for 'Save the World'...")
    results = client_b.query(vec, k=1)
    top_meta = results[0][2]
    print(f" > Found: {top_meta}")
    
    if top_meta.get("mission") == "Save the World":
        print(" > [OK] Content Integrity Verified.")
    else:
         print(" > [FAIL] Content Corrupted.")

    print("\n=== Test Complete ===")
    # Threads die on exit

if __name__ == "__main__":
    main()
