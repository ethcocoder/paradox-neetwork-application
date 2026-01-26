"""Paradox Transport Protocol (PTP) Implementation
Implements efficient latent vector transmission with compression and encryption.
Based on documentation.md specification.
"""
import numpy as np
import gzip
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class PTPMessage:
    """
    Paradox Transport Protocol Message Structure
    Transmits semantic meaning (latent vectors) instead of raw data.
    """
    version: str = "1.0"
    message_id: str = ""
    sender_id: str = ""
    receiver_id: str = ""
    intent_type: str = "textual"  # textual, visual, audio, situational, temporal, emergency
    latent_vector: Optional[np.ndarray] = None
    temporal_delta: Optional[np.ndarray] = None
    priority: int = 0  # 0=normal, 1=high, 2=urgent, 3=emergency
    integrity_hash: str = ""
    encrypted: bool = False
    metadata: Dict[str, Any] = None
    timestamp: int = 0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp == 0:
            self.timestamp = int(datetime.utcnow().timestamp())


class PTPProtocol:
    """Paradox Transport Protocol - Efficient latent transmission"""
    
    # Compression settings
    QUANTIZATION_BITS = 8  # 32-bit → 8-bit quantization
    SPARSITY_THRESHOLD = 0.01  # Remove values < 0.01
    
    def __init__(self):
        pass
    
    # ==================== Vector Compression ====================
    
    def quantize_vector(self, vector: np.ndarray, bits: int = 8) -> np.ndarray:
        """
        Quantize 32-bit floats to lower precision (8-bit default).
        Reduces size by 75% while preserving semantic meaning.
        """
        # Normalize to [0, 1]
        v_min, v_max = vector.min(), vector.max()
        normalized = (vector - v_min) / (v_max - v_min + 1e-10)
        
        # Quantize to n-bit integers
        max_val = (2 ** bits) - 1
        quantized = np.round(normalized * max_val).astype(np.uint8)
        
        return quantized, v_min, v_max
    
    def dequantize_vector(self, quantized: np.ndarray, v_min: float, v_max: float) -> np.ndarray:
        """Restore quantized vector to float32"""
        max_val = (2 ** 8) - 1
        normalized = quantized.astype(np.float32) / max_val
        return normalized * (v_max - v_min) + v_min
    
    def sparsify_vector(self, vector: np.ndarray, threshold: float = 0.01) -> tuple:
        """
        Remove near-zero values for additional compression.
        Returns sparse representation: (indices, values)
        """
        mask = np.abs(vector) >= threshold
        indices = np.where(mask)[0]
        values = vector[mask]
        return indices, values, vector.shape
    
    def desparsify_vector(self, indices: np.ndarray, values: np.ndarray, shape: tuple) -> np.ndarray:
        """Restore sparse vector"""
        vector = np.zeros(shape, dtype=np.float32)
        vector[indices] = values
        return vector
    
    def compress_vector(self, vector: np.ndarray) -> bytes:
        """
        Full compression pipeline:
        1. Quantization (32-bit → 8-bit)
        2. Sparsification (remove near-zero)
        3. gzip compression
        
        Target: 512D vector → 1-4 KB transmitted
        """
        # Step 1: Quantize
        quantized, v_min, v_max = self.quantize_vector(vector, bits=self.QUANTIZATION_BITS)
        
        # Step 2: Sparsify
        indices, values, shape = self.sparsify_vector(quantized, threshold=self.SPARSITY_THRESHOLD)
        
        # Create compressed payload
        payload = {
            "indices": indices.tolist(),
            "values": values.tolist(),
            "shape": shape,
            "v_min": float(v_min),
            "v_max": float(v_max)
        }
        
        # Step 3: gzip
        json_bytes = json.dumps(payload).encode('utf-8')
        compressed = gzip.compress(json_bytes, compresslevel=9)
        
        return compressed
    
    def decompress_vector(self, compressed: bytes) -> np.ndarray:
        """Decompress vector from PTP payload"""
        # Step 1: gunzip
        json_bytes = gzip.decompress(compressed)
        payload = json.loads(json_bytes.decode('utf-8'))
        
        # Step 2: Desparsify
        indices = np.array(payload["indices"], dtype=np.int32)
        values = np.array(payload["values"], dtype=np.uint8)
        shape = tuple(payload["shape"])
        quantized = self.desparsify_vector(indices, values, shape)
        
        # Step 3: Dequantize
        vector = self.dequantize_vector(quantized, payload["v_min"], payload["v_max"])
        
        return vector
    
    # ==================== Message Serialization ====================
    
    def serialize_message(self, message: PTPMessage) -> bytes:
        """
        Serialize PTPMessage to bytes for transmission.
        Compresses latent vectors and temporal deltas.
        """
        # Prepare message dict
        msg_dict = {
            "version": message.version,
            "message_id": message.message_id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "intent_type": message.intent_type,
            "priority": message.priority,
            "encrypted": message.encrypted,
            "metadata": message.metadata,
            "timestamp": message.timestamp
        }
        
        # Compress latent vector
        if message.latent_vector is not None:
            msg_dict["latent_vector"] = self.compress_vector(message.latent_vector).hex()
        
        # Compress temporal delta if present
        if message.temporal_delta is not None:
            msg_dict["temporal_delta"] = self.compress_vector(message.temporal_delta).hex()
        
        # Compute integrity hash
        content = json.dumps(msg_dict, sort_keys=True).encode('utf-8')
        msg_dict["integrity_hash"] = hashlib.sha256(content).hexdigest()
        
        # Final serialization
        return json.dumps(msg_dict).encode('utf-8')
    
    def deserialize_message(self, data: bytes) -> PTPMessage:
        """Deserialize bytes back to PTPMessage"""
        msg_dict = json.loads(data.decode('utf-8'))
        
        # Decompress latent vector
        latent_vector = None
        if "latent_vector" in msg_dict:
            compressed = bytes.fromhex(msg_dict["latent_vector"])
            latent_vector = self.decompress_vector(compressed)
        
        # Decompress temporal delta
        temporal_delta = None
        if "temporal_delta" in msg_dict:
            compressed = bytes.fromhex(msg_dict["temporal_delta"])
            temporal_delta = self.decompress_vector(compressed)
        
        return PTPMessage(
            version=msg_dict["version"],
            message_id=msg_dict["message_id"],
            sender_id=msg_dict["sender_id"],
            receiver_id=msg_dict["receiver_id"],
            intent_type=msg_dict["intent_type"],
            latent_vector=latent_vector,
            temporal_delta=temporal_delta,
            priority=msg_dict["priority"],
            integrity_hash=msg_dict.get("integrity_hash", ""),
            encrypted=msg_dict.get("encrypted", False),
            metadata=msg_dict.get("metadata", {}),
            timestamp=msg_dict["timestamp"]
        )
    
    # ==================== Differential Encoding ====================
    
    def compute_delta(self, previous_vector: np.ndarray, current_vector: np.ndarray) -> np.ndarray:
        """
        Compute semantic delta between sequential messages.
        Only transmit changes, not full vector.
        """
        return current_vector - previous_vector
    
    def apply_delta(self, previous_vector: np.ndarray, delta: np.ndarray) -> np.ndarray:
        """Apply delta to reconstruct current vector"""
        return previous_vector + delta
    
    # ==================== Bandwidth Estimation ====================
    
    def estimate_bandwidth(self, message: PTPMessage) -> int:
        """Estimate bandwidth usage in bytes"""
        serialized = self.serialize_message(message)
        return len(serialized)
    
    def get_compression_ratio(self, original_vector: np.ndarray, compressed: bytes) -> float:
        """Calculate compression ratio"""
        original_size = original_vector.nbytes
        compressed_size = len(compressed)
        return original_size / compressed_size


# Global PTP protocol instance
ptp_protocol = PTPProtocol()
