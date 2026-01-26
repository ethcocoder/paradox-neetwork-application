import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.media.clip_module import CLIPEncoder

def main():
    print("=== Paradox Complex Intelligence Test: 'The Evolution of Ideas' ===")
    
    # 1. Setup Engine with CLIP (High Intelligence)
    try:
        print("Loading CLIP (Unified Brain)...")
        encoder = CLIPEncoder()
        engine = LatentMemoryEngine(dimension=encoder.dimension)
        engine.set_encoder(encoder)
    except Exception as e:
        print(f"[!] Failed to load CLIP: {e}")
        return

    # 2. Add Knowledge Base (The "World Model")
    print("\n[Learning] Memorizing human inventions...")
    inventions = [
        "Stone Tool", "Fire", "Wheel", "Writing",
        "Steam Engine", "Electricity", "Telephone", "Radio",
        "Car", "Airplane", "Rocket",
        "Computer", "Internet", "Smartphone", "Virtual Reality",
        "Artificial Intelligence", "Quantum Computer", "Dyson Sphere",
        "Neural Link", "Teleportation"
    ]
    
    for inv in inventions:
        # We store the text itself as metadata
        engine.add(inv, {"name": inv})
        
    print(f"Stored {len(inventions)} concepts.")
    
    # ====================================================
    # Task 1: Imagination (Concept Blending)
    # ====================================================
    print("\n--- Task 1: Imagination (The Smartphone Test) ---")
    print("Blending 'Telephone' + 'Computer'...")
    
    # Use the high-level API
    new_idea_vec = engine.imagine("Telephone", "Computer", ratio=0.5)
    
    # Search for what this new idea is closest to
    print("Searching for the result...")
    results = engine.query(new_idea_vec, k=3)
    
    for idx, dist, meta in results:
        print(f" > Match: '{meta['name']}' (Dist: {dist:.4f})")
        
    top_match = results[0][2]['name']
    if top_match in ["Smartphone", "Internet", "Computer"]:
        print("[OK] Paradox imagined a Smartphone (or related tech)!")
    else:
        print(f"[!] Result '{top_match}' is interesting, but not the target.")

    # ====================================================
    # Task 2: Temporal Prediction (Future Forecasting)
    # ====================================================
    print("\n--- Task 2: Temporal Prediction (The Future of Tech) ---")
    
    history_concepts = ["Fire", "Steam Engine", "Electricity", "Computer", "Internet"]
    print(f"History Trajectory: {history_concepts}")
    
    # Encode history
    history_vecs = [encoder.encode(c) for c in history_concepts]
    
    # Predict next step
    print("Predicting the Next Major Invention...")
    future_vecs = engine.predict_future(history_vecs, steps=1)
    
    # Decode Prediction (by searching)
    results = engine.query(future_vecs[0], k=3)
    
    for idx, dist, meta in results:
        print(f" > Predicted: '{meta['name']}' (Dist: {dist:.4f})")
        
    top_pred = results[0][2]['name']
    print(f"\nParadox thinks the future is: '{top_pred}'")
    
    if top_pred in ["Artificial Intelligence", "Neural Link", "Virtual Reality", "Quantum Computer", "Internet"]:
        print("[OK] Paradox predicted a logical high-tech future!")
    else:
        print("[!] Prediction is unexpected.")

if __name__ == "__main__":
    main()
