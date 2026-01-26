"""Messaging API endpoints - Core PNA functionality"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import numpy as np

from app.core.security import get_current_user
from app.core.traffic_router import traffic_router
from app.services.latent_encoder import latent_encoder
from app.services.latent_decoder import latent_decoder
from app.services.ptp_protocol import PTPMessage, ptp_protocol
from app.models.message import IntentType

router = APIRouter(prefix="/messages", tags=["messages"])


# ==================== Request/Response Models ====================

class SendMessageRequest(BaseModel):
    """Send message request"""
    receiver_id: str = Field(..., description="Receiver user ID")
    intent_type: IntentType = Field(..., description="Message intent type")
    content: Dict[str, Any] = Field(..., description="Message content")
    priority: int = Field(0, ge=0, le=3, description="Priority (0=normal, 3=emergency)")


class MessageResponse(BaseModel):
    """Message response"""
    message_id: str
    status: str
    estimated_delivery: Optional[str] = None
    data_used_bytes: int


class ReceivedMessage(BaseModel):
    """Received message format"""
    message_id: str
    sender_id: str
    intent_type: str
    content: Dict[str, Any]
    timestamp: str
    delivered_at: Optional[str] = None
    read_at: Optional[str] = None


# ==================== Routes ====================

@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message via PTP protocol.
    
    **Lane**: Lane A (Zero-Rated) - core.pna.et  
    **Operation**: message_send  
    **Bandwidth**: ~2-5 KB per message
    
    Process:
    1. Encode content to latent vector
    2. Compress via PTP protocol
    3. Encrypt with receiver's public key
    4. Queue for delivery
    """
    # Enforce traffic routing to zero-rated domain
    traffic_router.enforce_traffic_separation(
        domain=traffic_router.get_domain_for_operation("message_send"),
        operation="message_send"
    )
    
    try:
        # Step 1: Encode content to latent vector
        latent_vector = latent_encoder.encode_message(
            content=request.content,
            intent_type=request.intent_type.value
        )
        
        # Step 2: Create PTP message
        message_id = str(uuid.uuid4())
        ptp_msg = PTPMessage(
            message_id=message_id,
            sender_id=current_user["user_id"],
            receiver_id=request.receiver_id,
            intent_type=request.intent_type.value,
            latent_vector=latent_vector,
            priority=request.priority,
            metadata={
                "original_format": request.content.get("format", "unknown"),
                "reconstruction_hint": request.content.get("hint", "")
            }
        )
        
        # Step 3: Serialize and compress
        serialized = ptp_protocol.serialize_message(ptp_msg)
        data_used = len(serialized)
        
        # Step 4: TODO - Store in database and message queue
        # For now, just return success
        
        # Calculate estimated delivery time based on priority
        delivery_map = {0: 30, 1: 5, 2: 1, 3: 0}  # seconds
        estimated_delivery = datetime.utcnow().timestamp() + delivery_map[request.priority]
        
        return MessageResponse(
            message_id=message_id,
            status="queued",
            estimated_delivery=datetime.fromtimestamp(estimated_delivery).isoformat(),
            data_used_bytes=data_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/receive", response_model=List[ReceivedMessage])
async def receive_messages(
    since: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve messages for current user.
    
    **Lane**: Lane A (Zero-Rated) - core.pna.et  
    **Operation**: message_receive  
    **Bandwidth**: Receiver uses ZERO data (zero-rated)
    
    Returns latent vectors that are reconstructed on client device.
    """
    # Enforce zero-rated routing
    traffic_router.enforce_traffic_separation(
        domain=traffic_router.get_domain_for_operation("message_receive"),
        operation="message_receive"
    )
    
    # TODO: Fetch messages from database
    # For now, return mock data
    
    return []


@router.get("/history/{contact_id}", response_model=List[ReceivedMessage])
async def get_message_history(
    contact_id: str,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Get message history with a specific contact.
    
    **Lane**: Lane A (Zero-Rated)
    **Operation**: message_history
    """
    traffic_router.enforce_traffic_separation(
        domain=traffic_router.get_domain_for_operation("message_history"),
        operation="message_history"
    )
    
    # TODO: Fetch from database
    return []


@router.post("/read/{message_id}")
async def mark_as_read(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark message as read.
    
    **Lane**: Lane A (Zero-Rated)
    """
    # TODO: Update database
    return {"message_id": message_id, "read_at": datetime.utcnow().isoformat()}


@router.post("/send/image")
async def send_image(
    receiver_id: str,
    image: UploadFile = File(...),
    priority: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Send image message.
    Automatically encodes to CLIP latent space.
    
    **Lane**: Lane A (Zero-Rated)
    **Bandwidth**: ~3-4 KB (vs 2-10 MB for raw image!)
    """
    traffic_router.enforce_traffic_separation(
        domain=traffic_router.get_domain_for_operation("message_send"),
        operation="message_send"
    )
    
    # Read image bytes
    image_bytes = await image.read()
    
    # Encode to latent vector
    latent_vector = latent_encoder.encode_image_bytes(image_bytes)
    
    # Create PTP message
    message_id = str(uuid.uuid4())
    ptp_msg = PTPMessage(
        message_id=message_id,
        sender_id=current_user["user_id"],
        receiver_id=receiver_id,
        intent_type="visual",
        latent_vector=latent_vector,
        priority=priority,
        metadata={
            "original_format": image.content_type,
            "reconstruction_hint": "image"
        }
    )
    
    # Serialize
    serialized = ptp_protocol.serialize_message(ptp_msg)
    
    return MessageResponse(
        message_id=message_id,
        status="queued",
        data_used_bytes=len(serialized)
    )


@router.get("/stats")
async def get_messaging_stats(current_user: dict = Depends(get_current_user)):
    """
    Get messaging statistics for current user.
    
    Shows bandwidth savings and message counts.
    """
    # TODO: Query database for actual stats
    return {
        "total_messages_sent": 0,
        "total_messages_received": 0,
        "total_bandwidth_used_kb": 0,
        "bandwidth_saved_vs_traditional_percent": 95,
        "zero_rated_traffic_kb": 0
    }
