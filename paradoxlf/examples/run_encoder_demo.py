import sys
import os

# Ensure we can import the local package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox.engine import LatentMemoryEngine
from paradox.encoder import RandomEncoder

def main():
    print("=== Paradox Auto-Encoder Demo ===")
    
    # Initialize with 4096 dimensions (simulating a large LLM embedding)
    dim = 64
    engine = LatentMemoryEngine(dimension=dim, backend="numpy")
    
    # Set a mock encoder which takes "Text" strings and turns them into random vectors
    encoder = RandomEncoder(dim)
    engine.set_encoder(encoder)
    
    # Now we can add raw text!
    raw_inputs = [
        "The quick brown fox",
        "Jumps over the lazy dog",
        "Paradox engines are cool",
        "Latent space simulation"
    ]
    
    print("Adding raw text data (auto-encoded)...")
    for text in raw_inputs:
        eid = engine.add(text, {"content": text})
        print(f"Stored '{text}' as ID {eid}")
        
    print(f"\nTotal stored: {engine.count}")
    
    # Query with text (auto-encoded)
    query_text = "Space simulation"
    logger_vec = encoder.encode(query_text) # In a real system, query() should also accept raw data if encoder exists
    
    # Let's verify we can query manually first
    results = engine.query(logger_vec, k=1)
    print(f"\nNearest to '{query_text}':")
    for rid, dist, meta in results:
        print(f" - Found: '{meta['content']}' (ID: {rid})")

if __name__ == "__main__":
    main()
