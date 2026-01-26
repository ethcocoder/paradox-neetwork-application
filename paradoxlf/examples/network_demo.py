import sys
import os
import time
import numpy as np
import threading
import uvicorn

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.distributed import ShardServer, RemoteShard

def run_server_thread():
    # Start server on a background thread
    print("[Demo] Starting Server on Port 8123...")
    server = ShardServer(dimension=64, shard_id="demo_server")
    # Using uvicorn directly with specific config to run in thread
    config = uvicorn.Config(server.app, host="127.0.0.1", port=8123, log_level="error")
    server_instance = uvicorn.Server(config)
    server_instance.run()

def main():
    print("=== Paradox Networked Memory Demo (v0.12.1) ===")
    
    # 1. Start Server in Background
    t = threading.Thread(target=run_server_thread, daemon=True)
    t.start()
    time.sleep(2) # Wait for boot
    
    # 2. Connect Client
    print("\n[Client] Connecting to Remote Shard...")
    client = RemoteShard(host="127.0.0.1", port=8123)
    
    # 3. Add Data Remotely
    print("\n[Client] Sending Data over HTTP...")
    vec = np.random.rand(64).astype(np.float32)
    client.add(vec, {"msg": "Hello from Network!"})
    print(" > Data Sent.")
    
    # 4. Query Remotely
    print("\n[Client] Querying Remote Shard...")
    results = client.query(vec, k=1)
    
    print(" > Result Received:")
    for idx, dist, meta in results:
        print(f"   - {meta['msg']} (Dist: {dist:.4f})")
        
    print("\n[Success] Networked Latent Memory Operational.")

if __name__ == "__main__":
    main()
