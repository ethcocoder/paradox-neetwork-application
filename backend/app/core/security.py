"""Security utilities: JWT, encryption, authentication"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import numpy as np
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()


class SecurityService:
    """Handles authentication, encryption, and security operations"""
    
    def __init__(self):
        self.jwt_secret = settings.jwt_secret
        self.jwt_algorithm = settings.jwt_algorithm
        self.jwt_expiration = timedelta(hours=settings.jwt_expiration_hours)
    
    # ==================== Password Hashing ====================
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    # ==================== JWT Tokens ====================
    
    def create_access_token(self, user_id: str, phone_number: str) -> str:
        """Generate JWT access token for authentication"""
        expire = datetime.utcnow() + self.jwt_expiration
        payload = {
            "user_id": user_id,
            "phone_number": phone_number,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def decode_token(self, token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    # ==================== RSA Key Generation ====================
    
    def generate_rsa_keypair(self) -> tuple[str, str]:
        """Generate RSA-4096 keypair for E2E encryption"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return public_pem, private_pem
    
    # ==================== End-to-End Encryption ====================
    
    def encrypt_vector(
        self, 
        vector: np.ndarray, 
        receiver_public_key_pem: str
    ) -> dict:
        """
        E2E encrypt latent vector with receiver's public key.
        Uses hybrid encryption: AES-256-GCM for data + RSA-4096 for key exchange.
        """
        # Convert vector to bytes
        vector_bytes = vector.tobytes()
        
        # Generate random AES key
        aes_key = os.urandom(32)  # 256 bits
        
        # Generate random IV for GCM mode
        iv = os.urandom(12)  # 96 bits for GCM
        
        # Encrypt vector with AES-GCM
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_vector = encryptor.update(vector_bytes) + encryptor.finalize()
        tag = encryptor.tag
        
        # Load receiver's public key
        public_key = serialization.load_pem_public_key(
            receiver_public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        # Encrypt AES key with RSA
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            "encrypted_vector": encrypted_vector,
            "encrypted_key": encrypted_aes_key,
            "iv": iv,
            "tag": tag,
            "vector_shape": vector.shape,
            "vector_dtype": str(vector.dtype)
        }
    
    def decrypt_vector(
        self, 
        encrypted_data: dict, 
        private_key_pem: str
    ) -> np.ndarray:
        """Decrypt latent vector using receiver's private key"""
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # Decrypt AES key with RSA
        aes_key = private_key.decrypt(
            encrypted_data["encrypted_key"],
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt vector with AES-GCM
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(encrypted_data["iv"], encrypted_data["tag"]),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        vector_bytes = decryptor.update(encrypted_data["encrypted_vector"]) + decryptor.finalize()
        
        # Reconstruct numpy array
        vector = np.frombuffer(vector_bytes, dtype=encrypted_data["vector_dtype"])
        return vector.reshape(encrypted_data["vector_shape"])
    
    # ==================== Integrity Verification ====================
    
    def compute_integrity_hash(self, data: bytes) -> str:
        """Compute SHA-256 hash for integrity verification"""
        from hashlib import sha256
        return sha256(data).hexdigest()
    
    def verify_integrity(self, data: bytes, expected_hash: str) -> bool:
        """Verify data integrity"""
        computed_hash = self.compute_integrity_hash(data)
        return computed_hash == expected_hash


# Global security service instance
security_service = SecurityService()


# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Extract and validate user from JWT token"""
    token = credentials.credentials
    payload = security_service.decode_token(token)
    return payload
