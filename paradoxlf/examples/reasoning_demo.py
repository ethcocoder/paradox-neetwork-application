import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.media.text import TransformerTextEncoder
from paradox.mixer import ParadoxMixer

def main():
    print("=== Paradox Semantic Reasoning (King - Man + Woman) Demo ===")
    
    # 1. Setup Engine
    try:
        encoder = TransformerTextEncoder(model_name='all-MiniLM-L6-v2')
        engine = LatentMemoryEngine(dimension=encoder.dimension) # 384
        engine.set_encoder(encoder)
    except ImportError:
        print("[!] Requires 'sentence-transformers'. Install paradoxlf[ai].")
        return

    # 2. Train Memory with Concepts
    concepts = [
        "king", "man", "woman", "queen", 
        "prince", "princess", "castle", "throne"
    ]
    
    print("\nMemorizing Concepts:")
    for c in concepts:
        engine.add(c, {"text": c})
        print(f" - {c}")
        
    # 3. Perform Latent Arithmetic
    # We want: King - Man + Woman = ? (Should be Queen)
    
    vec_king = encoder.encode("king")
    vec_man = encoder.encode("man")
    vec_woman = encoder.encode("woman")
    
    print("\nCalculating: King - Man + Woman...")
    
    # Step 1: King - Man
    vec_diff = ParadoxMixer.subtract(vec_king, vec_man)
    
    # Step 2: Result + Woman
    vec_royal_female = ParadoxMixer.add(vec_diff, vec_woman)
    
    # 4. Search for the result
    print("Searching Memory for Result...")
    results = engine.query(vec_royal_female, k=3, metric='cosine')
    
    for idx, dist, meta in results:
        print(f" > Found: '{meta['text']}' (Dist: {dist:.4f})")
        
    # Validation
    top_match = engine.objects[results[0][0]]['text']
    if top_match == "queen":
        print("\n✅ SUCCESS: Paradox correctly reasoned that King - Man + Woman = Queen!")
    else:
        print(f"\n⚠️ Result: '{top_match}'. (Model might be too small or noise high)")

if __name__ == "__main__":
    main()
