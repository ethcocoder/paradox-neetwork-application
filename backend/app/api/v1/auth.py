"""Authentication API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime, timedelta

from app.core.security import security_service
from app.core.traffic_router import traffic_router

router = APIRouter(prefix="/auth", tags=["authentication"])


# ==================== Request/Response Models ====================

class RegisterRequest(BaseModel):
    """User registration request"""
    phone_number: str = Field(..., description="Phone number in E.164 format (+251...)")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    username: Optional[str] = Field(None, description="Optional display name")


class LoginRequest(BaseModel):
    """User login request"""
    phone_number: str = Field(..., description="Phone number")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    phone_number: str
    role: str
    subscription_tier: str
    public_key: Optional[str] = None


# ==================== Routes ====================

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    **Lane**: Lane A (Zero-Rated) - core.pna.et
    **Operation**: user_registration
    """
    # Enforce traffic routing
    traffic_router.enforce_traffic_separation(
        domain=traffic_router.get_domain_for_operation("message_send"),  # Using message_send as proxy
        operation="message_send"
    )
    
    # TODO: Check if phone number already exists in database
    # For now, mock implementation
    
    # Hash password
    password_hash = security_service.hash_password(request.password)
    
    # Generate RSA keypair for E2E encryption
    public_key, private_key = security_service.generate_rsa_keypair()
    
    # Create user  (mock - should save to database)
    user_id = str(uuid.uuid4())
    
    # Generate JWT token
    access_token = security_service.create_access_token(
        user_id=user_id,
        phone_number=request.phone_number
    )
    
    return AuthResponse(
        access_token=access_token,
        user_id=user_id,
        phone_number=request.phone_number,
        role="sender",  # Default role
        subscription_tier="free",
        public_key=public_key
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login to existing account.
    
    **Lane**: Lane A (Zero-Rated) - core.pna.et
    **Operation**: user_authentication
    """
    # TODO: Look up user in database
    # TODO: Verify password with security_service.verify_password()
    # For now, mock implementation
    
    # Mock user lookup
    user_id = str(uuid.uuid4())
    
    # Generate token
    access_token = security_service.create_access_token(
        user_id=user_id,
        phone_number=request.phone_number
    )
    
    return AuthResponse(
        access_token=access_token,
        user_id=user_id,
        phone_number=request.phone_number,
        role="hybrid",
        subscription_tier="receiver_basic"
    )


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(security_service.decode_token)):
    """
    Refresh JWT token.
    
    **Lane**: Lane A (Zero-Rated)
    """
    # Generate new token
    new_token = security_service.create_access_token(
        user_id=current_user["user_id"],
        phone_number=current_user["phone_number"]
    )
    
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(security_service.decode_token)):
    """
    Get current user information.
    
    **Lane**: Lane A (Zero-Rated)
    """
    # TODO: Fetch full user info from database
    return current_user
