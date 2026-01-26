"""Latent Encoder Service
Integrates ParadoxLF framework to encode messages as semantic vectors.
"""
import sys
import os
import numpy as np
from typing import Dict, Any

# Add ParadoxLF to path
paradoxlf_path = os.path.join(os.path.dirname(__file__), "../../../paradoxlf")
sys.path.insert(0, paradoxlf_path)

from paradox.engine import LatentMemoryEngine
from paradox.media.clip_module import CLIPEncoder


class LatentEncoderService:
    """
    Encodes various content types to latent semantic vectors.
    Supports text, images, and situational contexts.
    """
    
    def __init__(self):
        """Initialize encoders"""
        try:
            # CLIP encoder for multimodal (text + images)
            self.clip_encoder = CLIPEncoder()
            self.engine = LatentMemoryEngine(dimension=self.clip_encoder.dimension)
            self.engine.set_encoder(self.clip_encoder)
            self.dimension = self.clip_encoder.dimension
        except Exception as e:
            print(f"Warning: Failed to load CLIP encoder: {e}")
            print("Falling back to mock encoder for development")
            self.clip_encoder = None
            self.engine = None
            self.dimension = 512  # Default dimension
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text message to semantic vector.
        Uses CLIP text encoder for semantic meaning extraction.
        """
        if self.clip_encoder:
            return self.clip_encoder.encode_text(text)
        else:
            # Mock encoder for development
            return self._mock_encode(text)
    
    def encode_image(self, image_path: str) -> np.ndarray:
        """
        Encode image to CLIP latent space.
        Captures visual semantic meaning.
        """
        if self.clip_encoder:
            return self.clip_encoder.encode_image(image_path)
        else:
            # Mock encoder
            return self._mock_encode(image_path)
    
    def encode_image_bytes(self, image_bytes: bytes) -> np.ndarray:
        """Encode image from bytes"""
        # Save temporarily and encode
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(image_bytes)
            temp_path = f.name
        
        try:
            vector = self.encode_image(temp_path)
        finally:
            os.unlink(temp_path)
        
        return vector
    
    def encode_situational(self, context: Dict[str, Any]) -> np.ndarray:
        """
        Encode situational state (location, context, status).
        Combines multiple signals into unified semantic vector.
        """
        # Combine context into text description
        parts = []
        if 'location' in context:
            parts.append(f"Location: {context['location']}")
        if 'activity' in context:
            parts.append(f"Activity: {context['activity']}")
        if 'status' in context:
            parts.append(f"Status: {context['status']}")
        
        text = " | ".join(parts)
        return self.encode_text(text)
    
    def encode_message(self, content: Dict[str, Any], intent_type: str) -> np.ndarray:
        """
        Main encoding dispatcher.
        Routes to appropriate encoder based on intent type.
        """
        if intent_type == "textual":
            return self.encode_text(content.get('text', ''))
        
        elif intent_type == "visual":
            if 'image_path' in content:
                return self.encode_image(content['image_path'])
            elif 'image_bytes' in content:
                return self.encode_image_bytes(content['image_bytes'])
            else:
                raise ValueError("Visual intent requires 'image_path' or 'image_bytes'")
        
        elif intent_type == "situational":
            return self.encode_situational(content)
        
        elif intent_type == "temporal":
            # Temporal is handled by tracking vector sequences
            return self.encode_text(content.get('text', ''))
        
        elif intent_type == "emergency":
            # Emergency messages encoded as text with high priority
            return self.encode_text(content.get('text', 'EMERGENCY'))
        
        else:
            raise ValueError(f"Unsupported intent type: {intent_type}")
    
    def _mock_encode(self, content: Any) -> np.ndarray:
        """
        Mock encoder for development without CLIP model.
        Generates deterministic random vectors.
        """
        import hashlib
        # Use content hash as seed for deterministic vectors
        seed = int(hashlib.md5(str(content).encode()).hexdigest()[:8], 16)
        np.random.seed(seed)
        vector = np.random.randn(self.dimension).astype(np.float32)
        # Normalize
        return vector / (np.linalg.norm(vector) + 1e-10)
    
    def get_dimension(self) -> int:
        """Get vector dimension"""
        return self.dimension


# Global encoder service instance
latent_encoder = LatentEncoderService()
