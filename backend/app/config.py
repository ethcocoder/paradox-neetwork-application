"""Application configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Paradox Network Application"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Dual-Lane Domain Configuration
    zero_rated_domain: str = "core.pna.et"
    normal_domain: str = "api.pna.et"
    
    # Database
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    
    # Vector Database
    pinecone_api_key: str
    pinecone_environment: str = "us-west1-gcp"
    pinecone_index_name: str = "pna-vectors"
    
    # Security
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Message Queue
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    
    # Ethio Telecom Integration
    telecom_partner: str = "ethio_telecom"
    zero_rating_enabled: bool = True
    
    # Rate Limiting
    rate_limit_per_minute: int = 10
    priority_rate_limit_per_minute: int = 5
    
    # File Upload
    max_upload_size_mb: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
