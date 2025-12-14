# 📝 Implementation Todo List (Next Steps)

## 1. Benchmarking & Profiling (The Baseline)
- [ ] **Create Benchmark Suite** (`examples/benchmark_scale.py`)
    - [ ] Measure `add()` throughput (item/sec) for 10k, 100k, 1M items.
    - [ ] Measure `query()` latency (ms) for 10k, 100k, 1M items (Exact Scan).
    - [ ] Measure memory usage (RAM per 1000 vectors).
- [ ] **Identify Hotspots**
    - [ ] Profile Python loops in `engine.py`.
    - [ ] Identify cost of HTTP overhead in `shards.py`.

## 2. Pluggable Indexing (The Skeleton)
- [ ] **Refactor `LatentMemoryEngine`**
    - [ ] Extract storage logic into `VectorStore` abstract base class.
    - [ ] Implement `FlatIndex` (Current NumPy implementation).
    - [ ] **Action:** Create `paradox/kernel/index.py`.
- [ ] **Integrate HNSW (The Muscle)**
    - [ ] `pip install hnswlib` (or faiss-cpu).
    - [ ] Implement `HNSWIndex` class inheriting from `VectorStore`.
    - [ ] Add `build_index()` and `save/load` methods.
    - [ ] Updates `query()` to use the graph search if index exists.

## 3. Rust Native Core (The Speed)
- [ ] **Setup Rust Environment**
    - [ ] Initialize `new --lib paradox_core`.
    - [ ] Configure `maturin` or `setuptools-rust` in `setup.py`.
- [ ] **Port Distance Functions**
    - [ ] Write `cosine_similarity` in Rust with SIMD.
    - [ ] Bind to Python via `PyO3`.
    - [ ] Replace `numpy.linalg.norm` calls in hot loops.

## 4. Metadata & Versioning (The Brain)
- [ ] **Update Vector Schema**
    - [ ] Modify `memory` dict to store `{"vector": ..., "meta": {"__v": 1, "__enc": "clip_v1", ...}}`.
- [ ] **Implement `ParadoxAdapter`**
    - [ ] Create `paradox/neural/adapter.py` (Simple PyTorch MLP).
    - [ ] Create generic training loop (`train_adapter(old_vecs, new_vecs)`).

## 5. Distributed Routing (The Network)
- [ ] **Shard Summaries**
    - [ ] Add method `shard.get_centroid()` (Mean of all local vectors).
- [ ] **Cluster Router**
    - [ ] Update `LatentCluster.query` to:
        1. Fetch centroids from all shards.
        2. Sort shards by distance to query vector.
        3. Query only top K shards (instead of all).

## 6. Hybrid Evolution (The Muse)
- [ ] **LLM Connector**
    - [ ] Create `paradox/connectors/llm.py`.
    - [ ] Implement `propose_mutation(text_description)` using broad API.
- [ ] **Integration**
    - [ ] Update `GeneticOptimizer` to allow `custom_mutation_function`.
