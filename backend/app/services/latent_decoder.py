"""Latent Decoder Service
Reconstructs messages from latent semantic vectors using ParadoxLF.
"""
import sys
import os
import numpy as np
from typing import Optional, Dict, Any

# Add ParadoxLF to path
paradoxlf_path = os.path.join(os.path.dirname(__file__), "../../../paradoxlf")
sys.path.insert(0, paradoxlf_path)

from paradox.engine import LatentMemoryEngine
from paradox.media.clip_module import CLIPEncoder


class LatentDecoderService:
    """
    Reconstructs content from latent vectors.
    Uses ParadoxLF's imagine() and conceptual_search() for reconstruction.
    """
    
    def __init__(self):
        """Initialize decoder with ParadoxLF engine"""
        try:
            self.clip_encoder = CLIPEncoder()
            self.engine = LatentMemoryEngine(dimension=self.clip_encoder.dimension)
            self.engine.set_encoder(self.clip_encoder)
            
            # Cache for frequent reconstructions
            self.text_cache = {}
            self.image_cache = {}
        except Exception as e:
            print(f"Warning: Failed to load decoder: {e}")
            self.clip_encoder = None
            self.engine = None
    
    def decode_text(self, vector: np.ndarray, use_cache: bool = True) -> str:
        """
        Reconstruct text from semantic vector.
        Uses conceptual search to find nearest text concept.
        """
        if self.engine is None:
            return "[Decoder not available]"
        
        # Check cache
        vector_hash = hash(vector.tobytes())
        if use_cache and vector_hash in self.text_cache:
            return self.text_cache[vector_hash]
        
        try:
            # Use conceptual search to find nearest concept
            results = self.engine.conceptual_search(vector, k=1)
            if results and len(results) > 0:
                text = results[0][2].get('text', '[Unable to decode]')
            else:
                text = '[Unable to decode]'
            
            # Cache result
            if use_cache:
                self.text_cache[vector_hash] = text
            
            return text
        except Exception as e:
            return f"[Decode error: {str(e)}]"
    
    def decode_image(self, vector: np.ndarray, reconstruction_hint: Optional[str] = None) -> bytes:
        """
        Generate image from CLIP latent vector.
        Uses ParadoxLF's imagine() for visual reconstruction.
        """
        if self.engine is None:
            # Return placeholder image bytes
            return self._generate_placeholder_image()
        
        try:
            # Use imagine() to reconstruct visual content
            # Note: This is a simplified version. Full implementation would use
            # diffusion models or GANs trained on CLIP latent space
            reconstructed = self.engine.imagine(vector, mode="visual")
            
            # Convert to bytes (depends on image format)
            # For now, return placeholder
            return self._generate_placeholder_image()
        except Exception as e:
            print(f"Image reconstruction error: {e}")
            return self._generate_placeholder_image()
    
    def decode_situational(self, vector: np.ndarray) -> Dict[str, Any]:
        """
        Decode situational vector back to context.
        Returns structured data about location, activity, status.
        """
        # Decode to text first
        text = self.decode_text(vector)
        
        # Parse structured context
        # Simple implementation - can be enhanced with NLP
        context = {
            "raw_text": text,
            "location": "Unknown",
            "activity": "Unknown",
            "status": "Unknown"
        }
        
        # Basic parsing
        if "Location:" in text:
            parts = text.split("Location:")[1].split("|")[0].strip()
            context["location"] = parts
        
        return context
    
    def decode_message(
        self, 
        vector: np.ndarray, 
        intent_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main decoding dispatcher.
        Routes to appropriate decoder based on intent type.
        """
        metadata = metadata or {}
        
        if intent_type == "textual":
            return {
                "type": "text",
                "content": self.decode_text(vector),
                "metadata": metadata
            }
        
        elif intent_type == "visual":
            return {
                "type": "image",
                "content": self.decode_image(
                    vector, 
                    reconstruction_hint=metadata.get("reconstruction_hint")
                ),
                "metadata": metadata
            }
        
        elif intent_type == "situational":
            return {
                "type": "situational",
                "content": self.decode_situational(vector),
                "metadata": metadata
            }
        
        elif intent_type in ["temporal", "emergency"]:
            return {
                "type": "text",
                "content": self.decode_text(vector),
                "metadata": metadata
            }
        
        else:
            raise ValueError(f"Unsupported intent type: {intent_type}")
    
    def _generate_placeholder_image(self) -> bytes:
        """Generate a simple placeholder image"""
        # Return minimal PNG placeholder
        # 1x1 gray pixel PNG
        return bytes.fromhex(
            '89504e470d0a1a0a0000000d494844520000000100000001'
            '08060000001f15c4890000000a49444154789c6300010000'
            '00050001fa5f64000000000049454e44ae426082'
        )
    
    def clear_cache(self):
        """Clear reconstruction cache"""
        self.text_cache.clear()
        self.image_cache.clear()


# Global decoder service instance
latent_decoder = LatentDecoderService()
