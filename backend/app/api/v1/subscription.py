"""Subscription management API"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

from app.core.security import get_current_user
from app.models.subscription import SubscriptionPlan, SubscriptionStatus

router = APIRouter(prefix="/subscription", tags=["subscription"])


# ==================== Request/Response Models ====================

class SubscriptionStatusResponse(BaseModel):
    """Subscription status response"""
    user_id: str
    plan: str
    status: str
    expires_at: Optional[str] = None
    auto_renew: bool
    days_remaining: int
    billing_provider: str


class PurchaseSubscriptionRequest(BaseModel):
    """Purchase subscription request"""
    plan: SubscriptionPlan = Field(..., description="Subscription plan to purchase")
    payment_method: str = Field(..., description="Payment method")
    telecom_account_id: Optional[str] = Field(None, description="Ethio Telecom account ID")


# ==================== Routes ====================

@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """
    Get current subscription status.
    
    **Lane**: Lane A (Zero-Rated) - core.pna.et
    **Operation**: subscription_validate
    """
    # TODO: Fetch from database
    # Mock response
    return SubscriptionStatusResponse(
        user_id=current_user["user_id"],
        plan="receiver_basic",
        status="active",
        expires_at=(datetime.utcnow() + timedelta(days=30)).isoformat(),
        auto_renew=True,
        days_remaining=30,
        billing_provider="telecom"
    )


@router.post("/purchase")
async def purchase_subscription(
    request: PurchaseSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Purchase or upgrade subscription.
    
    **Lane**: Lane B (Normal Internet) - api.pna.et
    **Operation**: subscription_purchase
    
    Uses normal internet to connect to payment providers.
    """
    # TODO: Integrate with payment provider
    # TODO: If telecom billing, integrate with Ethio Telecom API
    
    return {
        "subscription_id": "sub_12345",
        "status": "pending",
        "message": "Subscription purchase initiated. You will receive confirmation via SMS."
    }


@router.post("/cancel")
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """
    Cancel auto-renewal of subscription.
    
    **Lane**: Lane A (Zero-Rated)
    """
    # TODO: Update database
    return {
        "status": "cancelled",
        "message": "Auto-renewal has been cancelled. Your subscription will remain active until expiry."
    }


@router.get("/plans")
async def get_available_plans():
    """
    Get available subscription plans with pricing.
    
    **Lane**: Lane A (Zero-Rated)
    """
    return {
        "plans": [
            {
                "id": "sender_free",
                "name": "Free Sender",
                "price": 0,
                "currency": "ETB",
                "features": [
                    "Send messages using your data",
                    "Unlimited sending",
                    "Pay only for your mobile data usage"
                ]
            },
            {
                "id": "receiver_basic",
                "name": "Receiver Basic",
                "price": 50,  # ETB per month
                "currency": "ETB",
                "features": [
                    "Zero data cost for receiving",
                    "Unlimited message reception",
                    "Works in low-connectivity areas"
                ]
            },
            {
                "id": "receiver_premium",
                "name": "Receiver Premium",
                "price": 100,
                "currency": "ETB",
                "features": [
                    "All Basic features",
                    "Priority message sending",
                    "HD media mode (optional)"
                ]
            },
            {
                "id": "unlimited",
                "name": "Unlimited",
                "price": 200,
                "currency": "ETB",
                "features": [
                    "Unlimited send + receive",
                    "Zero data cost both ways",
                    "All premium features"
                ]
            }
        ]
    }
