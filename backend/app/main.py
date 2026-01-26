"""FastAPI Main Application
Paradox Network Application Backend
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.api.v1 import auth, messages, subscription
from app.core.traffic_router import traffic_router

# ==================== Application Setup ====================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Paradox Network Application - Latent Communication Platform",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# ==================== CORS Configuration ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Custom Middleware ====================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def traffic_lane_middleware(request: Request, call_next):
    """
    Traffic lane enforcement middleware.
    Tracks which domain is being accessed and validates operations.
    """
    # Extract domain from request(simplified - would use request.base_url in production)
    domain = request.headers.get("Host", settings.zero_rated_domain)
    
    # Add domain info to request state
    request.state.domain = domain
    request.state.is_zero_rated = domain == settings.zero_rated_domain
    
    response = await call_next(request)
    
    # Add traffic info headers
    response.headers["X-Traffic-Lane"] = "zero-rated" if request.state.is_zero_rated else "normal"
    response.headers["X-Domain"] = domain
    
    return response


# ==================== Exception Handlers ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


# ==================== Routes ====================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "zero_rated_domain": settings.zero_rated_domain,
        "normal_domain": settings.normal_domain,
        "telecom_partner": settings.telecom_partner,
        "zero_rating_enabled": settings.zero_rating_enabled
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/traffic/stats")
async def get_traffic_stats():
    """
    Get traffic statistics for all operations.
    Used for Ethio Telecom compliance reporting.
    """
    operations = [
        "message_send", "message_receive", "message_history",
        "subscription_validate", "app_update", "analytics_report"
    ]
    
    stats = {
        op: traffic_router.get_traffic_stats(op)
        for op in operations
    }
    
    return {
        "traffic_stats": stats,
        "zero_rating_enabled": settings.zero_rating_enabled,
        "telecom_partner": settings.telecom_partner
    }


# ==================== Include API Routes ====================

# API v1
app.include_router(auth.router, prefix="/v1")
app.include_router(messages.router, prefix="/v1")
app.include_router(subscription.router, prefix="/v1")


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    print(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    print(f"📡 Zero-Rated Domain: {settings.zero_rated_domain}")
    print(f"🌐 Normal Domain: {settings.normal_domain}")
    print(f"🔒 Zero-Rating Enabled: {settings.zero_rating_enabled}")
    print(f"📞 Telecom Partner: {settings.telecom_partner}")
    
    # TODO: Initialize database connections
    # TODO: Initialize Redis cache
    # TODO: Initialize vector database (Pinecone)
    # TODO: Initialize message queue


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    print("👋 Shutting down...")
    # TODO: Close database connections
    # TODO: Close Redis connections


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
