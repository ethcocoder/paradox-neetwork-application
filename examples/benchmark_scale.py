import sys
import os
import time
import numpy as np
import psutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def benchmark(n_items, dim=128):
    print(f"\n--- Benchmarking N={n_items}, Dim={dim} ---")
    
    # 1. Setup
    engine = LatentMemoryEngine(dimension=dim)
    vectors = np.random.normal(0, 1, (n_items, dim)).astype(np.float32)
    
    start_mem = get_memory_usage()
    
    # 2. Add (Throughput)
    t0 = time.time()
    # Batch add simulation (engine.add is single item, we optimize this test loop)
    # We will just inject directly for internal speed test to isolate "Engine Logic" from "Python Loop"
    # But to test *User Experience*, we use the public API.
    # Paradox Engine currently doesn't have bulk add. This is a finding!
    # We will loop.
    for i in range(n_items):
        engine.add(vectors[i], {"id": i})
    t_add = time.time() - t0
    
    mem_after = get_memory_usage()
    print(f"Insert Time: {t_add:.4f}s | Throughput: {n_items/t_add:.0f} vec/s")
    print(f"Memory Overhead: {mem_after - start_mem:.2f} MB")
    
    # 3. Query (Latency)
    query_vec = np.random.normal(0, 1, dim).astype(np.float32)
    
    t0 = time.time()
    k = 10
    results = engine.query(query_vec, k=k)
    t_query = time.time() - t0
    
    print(f"Query Latency (k={k}): {t_query*1000:.4f} ms")
    
    return t_add, t_query, (mem_after - start_mem)

def main():
    print("=== Paradox Hyperscale Benchmark (Baseline) ===")
    
    # Scales to test
    scales = [1000, 10000] 
    # Note: 100k or 1M might be too slow for a quick interaction test, 
    # but let's try 50k as the upper bound for this quick sanity check.
    scales.append(50000)

    for n in scales:
        benchmark(n)

if __name__ == "__main__":
    main()
