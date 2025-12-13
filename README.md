# Paradox: Latent Memory & Simulation Engine

**Paradox** is a lightweight, hardware-agnostic cognitive architecture for AI agents. It provides a dynamic "Latent Memory" that doesn't just store data but allows for active simulation, evolution, and proximity-based retrieval.

## 🚀 Key Features

*   **Hybrid Compute:** Automatically runs on **GPU (PyTorch)** if available, gracefully falls back to **CPU (NumPy/MMap)**.
*   **Active Inference:** Built-in `SimulationEnv` allows memory vectors to evolve over time based on physics-like dynamics.
*   **Infinite Scaling:** Supports disk-backed storage (`numpy.memmap`) for datasets larger than RAM.
*   **Plugin Architecture:** Easily plug in custom Neural Encoders (BERT, CLIP, VAEs) to auto-vectorize raw data.

## 🌍 Universal Applications

Paradox is not just for AI. It is a fundamental engine for **Massive Scale Simulation**:

### 1. 🏗️ Software Engineering
*   **Problem:** Traditional objects consume too much RAM.
*   **Paradox Solution:** Store object *recipes* (vectors) and reconstruct them only on demand.
*   **Use Case:** Massive game worlds (MMOs), entity management systems.

### 2. 🧬 Scientific Simulation
*   **Problem:** Simulating millions of neurons or particles requires Supercomputers.
*   **Paradox Solution:** Latent physics allows interacting with millions of entities using vector math.
*   **Use Case:** Neuroscience modeling, Traffic simulation, Ecosystem dynamics.

### 3. ☁️ Big Data & IoT
*   **Problem:** Searching billions of sensor logs is slow.
*   **Paradox Solution:** Proximity search finds anomalies instantly without scanning the whole DB.
*   **Use Case:** IoT anomaly detection, Real-time telemetry analysis.

### 4. 🎓 Education & Research
*   **Problem:** Students can't run "Big Tech" scale experiments on laptops.
*   **Paradox Solution:** Efficient storage allows billion-scale experimentation on consumer hardware.
*   **Use Case:** Teaching complex systems, Swarm intelligence research.

## 📦 Installation

```bash
git clone https://github.com/ethcocoder/paradoxlf.git
cd paradoxlf
pip install .
```

## ⚡ Quick Start

### 1. Basic Memory & Search
```python
from paradox.engine import LatentMemoryEngine

# Initialize (Auto-detects CPU vs GPU)
engine = LatentMemoryEngine(dimension=128)

# Add Data
engine.add([0.1, 0.5, ...], attributes={"name": "concept_A"})

# Search
results = engine.query([0.1, 0.5, ...], k=5)
print(results)
```

### 2. Auto-Encoding Raw Data
```python
from paradox.engine import LatentMemoryEngine
from paradox.encoder import BaseEncoder

# Define a custom encoder (e.g., wrapper around OpenAI/HuggingFace)
class MyTextEncoder(BaseEncoder):
    def encode(self, text):
        # ... logic to turn text into vector ...
        return vector

engine = LatentMemoryEngine(dimension=768)
engine.set_encoder(MyTextEncoder(768))

# Now simply add text!
engine.add("Artificial Intelligence is evolving", {"category": "AI"})
```

### 3. Simulation (The "Active" Part)
Paradox allows you to run simulations on your memory, letting concepts interact or drift.

```python
from paradox.simulation import SimulationEnv

def semantic_drift(vectors, dt, backend):
    return vectors * 0.01 # Simple example

sim = SimulationEnv(engine)
sim.run(steps=100, dynamics_fn=semantic_drift)
```

### 4. Visualization
Visualize your latent space in 2D using PCA or t-SNE.

```python
from paradox.visualization import LatentVisualizer

viz = LatentVisualizer(engine)
viz.plot_2d(method="pca", output_file="memory_map.png")
```

## 🤝 Contributing
Open source contributions are welcome. Please submit a PR for review.

## 📄 License
MIT License