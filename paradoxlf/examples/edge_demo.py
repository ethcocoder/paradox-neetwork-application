import sys
import os
import time
import threading
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.distributed import EdgeNode, ShardServer

# Mock Cloud Server
def run_mock_cloud(port):
    print(f"[Cloud] Starting Mainframe on port {port}...")
    server = ShardServer(dimension=64, shard_id="mainframe_01")
    server.run(port=port) # Blocking call, run in thread

def main():
    print("=== Paradox Edge Computing Demo (v0.14.0) ===")
    
    # 1. Start Cloud (Background)
    CLOUD_PORT = 9000
    t = threading.Thread(target=run_mock_cloud, args=(CLOUD_PORT,), daemon=True)
    t.start()
    time.sleep(2)
    
    # 2. Init Edge Device (e.g., a "Smart Camera")
    print("\n[Edge] Initializing Smart Camera Node...")
    edge = EdgeNode(cloud_host="127.0.0.1", cloud_port=CLOUD_PORT, local_dim=64)
    
    # 3. Simulate Data Stream
    print("\n[Stream] Processing Video Inputs...")
    
    # Scene A: Empty Room (Repeated)
    vec_room = np.random.rand(64).astype(np.float32)
    
    # Scene B: Intruder (Novel)
    vec_intruder = np.random.rand(64).astype(np.float32) + 5.0 # Distinctly different
    
    # Step 1: See Empty Room (New)
    print(" > Input: Empty Room")
    res = edge.perceive(vec_room, {"desc": "Empty Room T=0"})
    print(f"   Result: {res['status']} (Dist: {res['novelty_score']:.4f})")
    
    # Step 2: See Empty Room again (Known)
    # Add tiny noise to simulate sensor jitter
    vec_room_noisy = vec_room + np.random.normal(0, 0.01, 64).astype(np.float32)
    
    print(" > Input: Empty Room (Again)")
    res = edge.perceive(vec_room_noisy, {"desc": "Empty Room T=1"})
    print(f"   Result: {res['status']} (Dist: {res['novelty_score']:.4f})")
    # Should be "Known" and NOT synced.
    
    # Step 3: Intruder! (Novel)
    print(" > Input: INTRUDER ALERT")
    res = edge.perceive(vec_intruder, {"desc": "Intruder Detected!"})
    print(f"   Result: {res['status']} (Dist: {res['novelty_score']:.4f})")
    # Should be "Novel (Synced)"
    
    # 4. Verify Cloud Memory
    # Check if Cloud only learned the 2 important concepts, excluding the duplicate room frame.
    
    print("\n[Audit] Verifying Cloud Knowledge Base...")
    # Utilize internal client to check count
    cloud_count = edge.cloud_client.count()
    print(f" > Cloud Total Memories: {cloud_count}")
    
    if cloud_count == 2:
        print(" > [OK] Efficient Sync Confirmed (Ignored duplicate).")
    else:
        print(f" > [FAIL] Expected 2, got {cloud_count}")

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
