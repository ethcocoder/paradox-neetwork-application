"""User data model"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role types"""
    SENDER = "sender"
    RECEIVER = "receiver"
    HYBRID = "hybrid"


class User(Base):
    """User model for authentication and profiles"""
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), unique=True, nullable=False, index=True)
    username = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # Role management
    role = Column(SQLEnum(UserRole), default=UserRole.SENDER, nullable=False)
    
    # Subscription
    subscription_tier = Column(String(20), default="free")
    subscription_expires = Column(DateTime, nullable=True)
    
    # Security: RSA public key for E2E encryption
    public_key = Column(String(2048), nullable=True)
    
    # Device tracking
    device_ids = Column(ARRAY(String), default=[])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.phone_number} ({self.role})>"
    
    @property
    def is_receiver(self) -> bool:
        """Check if user has receiver privileges"""
        return self.role in [UserRole.RECEIVER, UserRole.HYBRID]
    
    @property
    def is_subscribed(self) -> bool:
        """Check if user has active subscription"""
        if self.subscription_expires is None:
            return False
        return datetime.utcnow() < self.subscription_expires
