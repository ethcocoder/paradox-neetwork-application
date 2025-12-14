import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.media.text import SimpleTextEncoder # Use Simple for speed/no-dep dependency check works

def main():
    print("=== Paradox Intelligence API Demo ===")
    
    # 1. Setup
    encoder = SimpleTextEncoder() # Dummy hash encoder for demo speed
    engine = LatentMemoryEngine(dimension=encoder.dimension)
    engine.set_encoder(encoder)
    
    # 2. Add Knowledge
    print("\n[Thinking] Learning concepts...")
    concepts = ["apple", "banana", "cherry", "date", "elderberry"]
    for c in concepts:
        engine.add(c, {"val": c})
        
    # 3. Conceptual Search
    print("\n1. Testing conceptual_search('banana')...")
    # This automatically handles encoding
    results = engine.conceptual_search("banana", k=1)
    print(f"   Found: {results[0][2]['val']}")
    
    # 4. Imagination
    print("\n2. Testing imagine('apple', 'cherry')...")
    # Blends vectors
    new_idea_vec = engine.imagine("apple", "cherry", ratio=0.5)
    print(f"   New Thought Vector (First 5 dims): {new_idea_vec[:5]}")
    
    # 5. Prediction
    print("\n3. Testing predict_future()...")
    # Simulate a sequence of thoughts
    history = [encoder.encode(c) for c in ["apple", "banana", "cherry"]]
    future = engine.predict_future(history, steps=1)
    
    # What is the future thought close to?
    res_future = engine.query(future[0], k=1)
    print(f"   Predicted Next Concept: {res_future[0][2]['val']} (Logic: A->B->C->...?)")

    print("\n[Success] High-level APIs are functional.")

if __name__ == "__main__":
    main()
