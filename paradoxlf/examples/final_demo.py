import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.media.clip_module import CLIPEncoder

# Optional visualization
try:
    import matplotlib.pyplot as plt
    VIZ = True
except ImportError:
    VIZ = False

def slow_print(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01)
    print("")

def main():
    print("=====================================================")
    print("   P A R A D O X   F I N A L   S H O W C A S E   ")
    print("      From Data -> Memory -> Intelligence        ")
    print("=====================================================\n")
    
    # 1. Initialize
    slow_print("[1/5] Initializing Cognitive Engine (w/ CLIP)...")
    try:
        encoder = CLIPEncoder()
        engine = LatentMemoryEngine(dimension=encoder.dimension)
        engine.set_encoder(encoder)
        print("      > Unified Multimodal Space: Ready (512-dim)")
    except Exception as e:
        print(f"[!] CLIP Failed: {e}")
        return

    # 2. Memory
    slow_print("\n[2/5] Memorizing World Concepts...")
    concepts = [
        "A peaceful forest", "A busy city street", "A red sports car", 
        "A fierce lion", "A cute kitten", "Stormy ocean waves",
        "A futuristic robot", "Ancient ruins", "A delicious pizza"
    ]
    for c in concepts:
        engine.add(c, {"desc": c})
        # print(f"      + '{c}'")
    print(f"      > Stored {len(concepts)} concepts in Latent Memory.")

    # 3. Semantic Search
    slow_print("\n[3/5] Testing Semantic Understanding...")
    query = "something dangerous and loud"
    slow_print(f"      Query: '{query}'")
    results = engine.conceptual_search(query, k=1)
    match = results[0][2]['desc']
    print(f"      > Best Match: '{match}' (It understood danger/loudness!)")
    
    # 4. Latent Imagination
    slow_print("\n[4/5] Testing Imagination (Blending)...")
    c1 = "A fierce lion"
    c2 = "A futuristic robot"
    slow_print(f"      Imagine: '{c1}' + '{c2}'")
    
    new_vec = engine.imagine(c1, c2, ratio=0.5)
    
    # What did we create?
    results = engine.conceptual_search(new_vec, k=3)
    print("      > Result looks like:")
    for idx, dist, meta in results:
        print(f"        - {meta['desc']} (Dist: {dist:.3f})")

    # 5. Temporal Prediction
    slow_print("\n[5/5] Testing Forethought (Temporal Prediction)...")
    # Trajectory: Calm -> Storm
    history_concepts = ["A peaceful forest", "Stormy ocean waves"]
    slow_print(f"      Trajectory: {history_concepts[0]} -> {history_concepts[1]} -> ???")
    
    # Encode
    history_vecs = [encoder.encode(c) for c in history_concepts]
    future_vec = engine.predict_future(history_vecs, steps=1)[0]
    
    # Search
    results = engine.query(future_vec, k=1)
    pred_match = results[0][2]['desc']
    print(f"      > Predicted Future State: '{pred_match}'")
    
    print("\n=====================================================")
    print("   P A R A D O X   S Y S T E M   O N L I N E     ")
    print("=====================================================")

if __name__ == "__main__":
    main()
