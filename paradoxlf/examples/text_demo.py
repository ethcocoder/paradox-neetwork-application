import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.media.text import SimpleTextEncoder, TransformerTextEncoder

def main():
    print("=== Paradox Text Intelligence Demo ===")
    
    # 1. Setup Engine
    engine = LatentMemoryEngine(dimension=384) # Standard for MiniLM-L6-v2
    
    # 2. Try to load Semantic Encoder
    try:
        print("Loading AI Text Encoder (sentence-transformers)...")
        encoder = TransformerTextEncoder(model_name='all-MiniLM-L6-v2')
        engine.set_encoder(encoder)
        print("Model Loaded Successfully!")
    except ImportError:
        print("\n[!] 'sentence-transformers' not found.")
        print("    Falling back to Simple ASCII Encoder (No semantic meaning).")
        print("    To fix: pip install paradoxlf[ai]")
        encoder = SimpleTextEncoder(dimension=384)
        engine.set_encoder(encoder)

    # 3. Memorize Concepts
    sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "A fast fox leaping over a dog.",
        "An apple a day keeps the doctor away.",
        "Fresh fruit is healthy for you.",
        "Quantum mechanics is confusing.",
    ]
    
    print(f"\nMemorizing {len(sentences)} concepts...")
    for s in sentences:
        uid = engine.add(s, {"text": s})
        print(f" - Stored: '{s}' (ID: {uid})")
        
    # 4. Semantic Search
    query = "healthy food"
    print(f"\nScanning Memory for: '[{query}]'...")
    
    # Encode query
    q_vec = encoder.encode(query)
    
    # Search
    results = engine.query(q_vec, k=3)
    
    print("\nResults (Nearest Semantic Neighbors):")
    for i, (uid, dist, attrs) in enumerate(results):
        text = attrs["text"]
        print(f" {i+1}. '{text}' (Distance: {dist:.4f})")
        
    print("\nAnalysis:")
    print("If semantic search works, 'Fresh fruit...' and 'An apple...' should be top results.")
    print("If using SimpleEncoder, results will be random/lexical.")

if __name__ == "__main__":
    main()
