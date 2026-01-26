"""Dual-Lane Traffic Router
Enforces strict separation between zero-rated (Lane A) and normal internet (Lane B) traffic.
Based on internet.md specification for Ethio Telecom integration.
"""
from typing import Literal, Set
from fastapi import HTTPException
from app.config import settings


class TrafficLane:
    """Traffic lane identifiers"""
    ZERO_RATED = "zero_rated"  # Lane A: core.pna.et
    NORMAL = "normal"           # Lane B: api.pna.et


class TrafficRouter:
    """Enforces dual-lane traffic separation per Ethio Telecom requirements"""
    
    # Lane A: Zero-rated domain traffic (FREE)
    ZERO_RATED_DOMAINS: Set[str] = {
        "core.pna.et",
        "ptp.pna.et"
    }
    
    # Lane A: Allowed traffic types (core communication)
    LANE_A_OPERATIONS: Set[str] = {
        "message_send",
        "message_receive",
        "message_history",
        "subscription_validate",
        "emergency_broadcast",
        "priority_send",
        "websocket_connect",
        "latent_transmission"
    }
    
    # Lane B: Normal internet traffic (uses user's data)
    LANE_B_OPERATIONS: Set[str] = {
        "app_update",
        "analytics_report",
        "external_api_call",
        "media_download_hd",  # HD mode (optional paid feature)
        "feedback_submission"
    }
    
    def __init__(self):
        self.zero_rating_enabled = settings.zero_rating_enabled
    
    def get_lane_for_operation(self, operation: str) -> str:
        """Determine which lane an operation should use"""
        if operation in self.LANE_A_OPERATIONS:
            return TrafficLane.ZERO_RATED
        elif operation in self.LANE_B_OPERATIONS:
            return TrafficLane.NORMAL
        else:
            raise ValueError(f"Unknown operation type: {operation}")
    
    def get_domain_for_operation(self, operation: str) -> str:
        """Get the appropriate domain for an operation"""
        lane = self.get_lane_for_operation(operation)
        
        if lane == TrafficLane.ZERO_RATED:
            return settings.zero_rated_domain
        else:
            return settings.normal_domain
    
    def validate_request_domain(self, domain: str, operation: str) -> bool:
        """
        Validate that the request domain matches the operation type.
        Prevents cross-lane contamination.
        """
        expected_domain = self.get_domain_for_operation(operation)
        
        if domain != expected_domain:
            raise HTTPException(
                status_code=403,
                detail=f"Operation '{operation}' not allowed on domain '{domain}'. "
                       f"Expected domain: '{expected_domain}'"
            )
        
        return True
    
    def is_zero_rated_traffic(self, operation: str) -> bool:
        """Check if an operation uses zero-rated traffic"""
        return operation in self.LANE_A_OPERATIONS
    
    def enforce_traffic_separation(self, domain: str, operation: str):
        """
        Main enforcement method. Raises HTTPException if traffic rules are violated.
        
        Rules:
        1. Core communication MUST use zero-rated domain
        2. External services MUST use normal domain
        3. No fallback or redirection between lanes
        4. No tunneling or proxy behavior
        """
        # Check if operation is allowed
        if operation not in (self.LANE_A_OPERATIONS | self.LANE_B_OPERATIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Unknown operation: {operation}"
            )
        
        # Validate domain matches operation
        self.validate_request_domain(domain, operation)
        
        # Additional checks for zero-rated traffic
        if self.is_zero_rated_traffic(operation):
            if not self.zero_rating_enabled:
                raise HTTPException(
                    status_code=503,
                    detail="Zero-rated service is currently unavailable"
                )
    
    def get_traffic_stats(self, operation: str) -> dict:
        """
        Get traffic statistics for an operation.
        Used for Ethio Telecom reporting and compliance.
        """
        lane = self.get_lane_for_operation(operation)
        return {
            "operation": operation,
            "lane": lane,
            "domain": self.get_domain_for_operation(operation),
            "zero_rated": self.is_zero_rated_traffic(operation),
            "billing": "free" if lane == TrafficLane.ZERO_RATED else "normal"
        }


# Global traffic router instance
traffic_router = TrafficRouter()
