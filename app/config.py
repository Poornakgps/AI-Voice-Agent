"""
Configuration settings for the Voice AI Restaurant Agent.
"""
import os
from pydantic import field_validator, validator, Field
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, Union
from functools import lru_cache

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Voice AI Restaurant Agent"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "A voice AI agent for restaurant interactions"
    DEBUG: bool = Field(False, description="Enable debug mode")
    LOG_LEVEL: str = "INFO"
    APP_ENV: str = "production"  # development, staging, production
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_ORG_ID: Optional[str] = os.environ.get("OPENAI_ORG_ID", None)
    
    # Twilio API settings
    TWILIO_API_KEY: str = os.environ.get("TWILIO_API_KEY", "")
    TWILIO_API_SECRET: str = os.environ.get("TWILIO_API_SECRET", "")
    TWILIO_PHONE_NUMBER: Optional[str] = os.environ.get("TWILIO_PHONE_NUMBER", None)
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # Storage settings
    STORAGE_TYPE: str = "local"  # local, gcs
    LOCAL_STORAGE_PATH: str = "./storage"
    GCS_BUCKET_NAME: Optional[str] = None
    
    # Ngrok settings
    NGROK_AUTHTOKEN: Optional[str] = None
    
    # Google Cloud settings
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_REGION: str = "us-central1"
    
    # Force using real OpenAI and Twilio APIs if keys are provided
    USE_REAL_APIS: bool = True
    
    # Validators
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        """
        Parse DEBUG environment variable as boolean.
        Accepts various string representations of boolean values.
        """
        if isinstance(v, str):
            return v.lower() in ("true", "1", "t", "yes", "y")
        return bool(v)
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Ensure LOG_LEVEL is a valid Python logging level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v
    
    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, v):
        """Ensure APP_ENV is a valid environment."""
        allowed_envs = ["development", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"APP_ENV must be one of {allowed_envs}")
        return v
    
    @field_validator("STORAGE_TYPE")
    @classmethod
    def validate_storage_type(cls, v):
        """Ensure STORAGE_TYPE is valid."""
        allowed_types = ["local", "gcs"]
        if v not in allowed_types:
            raise ValueError(f"STORAGE_TYPE must be one of {allowed_types}")
        return v
    
    @field_validator("OPENAI_API_KEY")
    @classmethod
    def check_openai_key(cls, v):
        """Validate OpenAI API key is properly set."""
        if v and v.strip() and "dummy" not in v:
            print("✅ OpenAI API key is configured properly")
            return v
        return ""
    
    @field_validator("TWILIO_API_KEY")
    @classmethod
    def check_twilio_key(cls, v):
        """Validate Twilio API key is properly set."""
        if v and v.strip() and "dummy" not in v:
            print("✅ Twilio API key is configured properly")
            return v
        return ""
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow any env var with a prefix of "DEBUG" to override the debug setting
        # This helps with Docker environment variables
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance.
    
    Using lru_cache to avoid reloading settings on every request.
    """
    return Settings()

# Export settings instance
settings = get_settings()

# For debug purposes
if __name__ == "__main__":
    print("API KEYS STATUS:")
    print(f"OpenAI API Key: {'Configured' if settings.OPENAI_API_KEY else 'Not configured'}")
    print(f"Twilio API Key: {'Configured' if settings.TWILIO_API_KEY else 'Not configured'}")
    print(f"Twilio API Secret: {'Configured' if settings.TWILIO_API_SECRET else 'Not configured'}")