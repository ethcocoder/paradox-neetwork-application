# Paradox V0.2.0 Roadmap: Multimedia Integration

## Goal
Expand Paradox from abstract math/text to full **Image & Video Latent Processing**.

## 1. Image Support
- [ ] **ImageEncoder:** Add support for loading images (JPG/PNG) and converting them to vectors.
    - [ ] Simple: Histogram/Pixel flattening (No AI).
    - [ ] Advanced: CLIP/ResNet embedding (AI).
- [ ] **ImageDecoder:** Reconstruct images from vectors (using Generative models or retrieval).

## 2. Video Support
- [ ] **Video as Simulation:** Treat a video file as a 1000-step simulation of image vectors.
- [ ] **Latent Interpolation:** "Dream" new frames between two existing video frames by simulating the vector path.

## 3. Libraries
- [ ] Add `Pillow` (PIL) for image handling.
- [ ] Add `torchvision` (optional) for neural encoders.

## 4. Demos
- [ ] `examples/image_search.py`: Find similar images in a folder.
- [ ] `examples/video_dream.py`: Interpolate between two images to make a video.
