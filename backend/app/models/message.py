"""Message data model"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum as SQLEnum, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.models.user import Base


class IntentType(str, enum.Enum):
    """Message intent types for latent classification"""
    TEXTUAL = "textual"
    VISUAL = "visual"
    AUDIO = "audio"
    SITUATIONAL = "situational"
    TEMPORAL = "temporal"
    EMERGENCY = "emergency"


class MessageStatus(str, enum.Enum):
    """Message delivery status"""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(Base):
    """Message model for PNA communication"""
    __tablename__ = "messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, index=True)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Intent classification
    intent_type = Column(SQLEnum(IntentType), nullable=False, default=IntentType.TEXTUAL)
    
    # Vector storage reference (actual vector stored in Pinecone)
    vector_id = Column(String(100), nullable=True)
    
    # Priority (0=normal, 1=high, 2=urgent, 3=emergency)
    priority = Column(Integer, default=0, nullable=False)
    
    # Integrity verification
    integrity_hash = Column(String(64), nullable=True)
    
    # Encrypted payload (for E2E encryption)
    encrypted_payload = Column(LargeBinary, nullable=True)
    
    # Status tracking
    status = Column(SQLEnum(MessageStatus), default=MessageStatus.QUEUED, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Metadata for reconstruction hints
    reconstruction_hint = Column(String(255), nullable=True)
    original_format = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<Message {self.message_id} {self.intent_type} {self.status}>"
    
    @property
    def is_priority(self) -> bool:
        """Check if message has priority delivery"""
        return self.priority > 0
    
    @property
    def delivery_time(self) -> int:
        """Get delivery time in seconds"""
        if self.delivered_at and self.timestamp:
            return int((self.delivered_at - self.timestamp).total_seconds())
        return 0
