# Paradox: Generative Latent Memory Framework

## Vision
“Store how data can be generated, not the data itself.”

Paradox is a dual-purpose software:  
- **Library:** Encode, store, retrieve, and query objects as latent vectors.  
- **Framework:** Manage object lifecycle, temporal evolution, and proximity-based simulation.

It allows simulation of millions/billions of objects on constrained hardware by storing **latent seeds** instead of full instances.

---

## Features

- Encode arbitrary Python objects into latent vectors
- On-demand reconstruction (decoder)
- Proximity-based search & clustering
- Temporal / dynamic simulation
- GPU acceleration via CuPy or PyTorch (optional)
- Disk-backed storage via memory mapping
- Plugin interface for custom encoders/decoders
- Integration with Antigravity IDE for live coding, visualization, and simulation control
- Production-ready deployment via PyPI or Docker

---

## Installation

### Local PC / Laptop
```bash
pip install .
