"""Subscription data model"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.models.user import Base


class SubscriptionPlan(str, enum.Enum):
    """Subscription plan types"""
    FREE = "sender_free"
    RECEIVER_BASIC = "receiver_basic"
    RECEIVER_PREMIUM = "receiver_premium"
    UNLIMITED = "unlimited"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BillingProvider(str, enum.Enum):
    """Payment/billing provider"""
    TELECOM = "telecom"  # Ethio Telecom billing
    STRIPE = "stripe"
    MANUAL = "manual"


class Subscription(Base):
    """Subscription model for receiver privileges"""
    __tablename__ = "subscriptions"
    
    subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Plan details
    plan = Column(SQLEnum(SubscriptionPlan), nullable=False, default=SubscriptionPlan.FREE)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    
    # Billing
    payment_method = Column(String(50), nullable=True)
    billing_provider = Column(SQLEnum(BillingProvider), nullable=False, default=BillingProvider.TELECOM)
    
    # Auto-renewal
    auto_renew = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Telecom integration
    telecom_account_id = Column(String(100), nullable=True)  # Ethio Telecom subscriber ID
    
    def __repr__(self):
        return f"<Subscription {self.plan} {self.status}>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return (
            self.status == SubscriptionStatus.ACTIVE and 
            self.end_date > datetime.utcnow()
        )
    
    @property
    def days_remaining(self) -> int:
        """Get number of days remaining"""
        if self.end_date:
            delta = self.end_date - datetime.utcnow()
            return max(0, delta.days)
        return 0
