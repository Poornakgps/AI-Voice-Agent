import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, Union
from functools import lru_cache

project_root = Path(__file__).parent.parent
env_path = project_root / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment from {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}")

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    APP_NAME: str = "Voice AI Restaurant Agent"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "A voice AI agent for restaurant interactions"
    DEBUG: bool = Field(False, description="Enable debug mode")
    LOG_LEVEL: str = "INFO"
    APP_ENV: str = "production"  # development, staging, production
    WEBHOOKBASE_URL: str = os.getenv("WEBHOOKBASE_URL", "http://localhost:8000")
    USE_MEDIA_STREAMS: bool = os.getenv("USE_MEDIA_STREAMS", "False").lower() in ("true", "1", "t", "yes")
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAIORG_ID: str = os.getenv("OPENAIORG_ID", "")
    
    TWILIO_API_KEY: str = ""
    TWILIO_API_SECRET: str = ""
    TWILIO_SID_KEY: str = os.environ.get("TWILIO_SID_KEY", "")
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    DATABASE_URL: str = "sqlite:///./test.db"
    
    STORAGE_TYPE: str = "local"  # local, gcs
    LOCAL_STORAGE_PATH: str = "./storage"
    GCS_BUCKET_NAME: Optional[str] = None
    
    NGROK_AUTHTOKEN: Optional[str] = None
    
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_REGION: str = "us-central1"
    
    USE_REAL_APIS: bool = True
    
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
    def validate_openai_key(cls, v):
        """Validate OpenAI API key is properly set."""
        if v and v.strip() and "dummy" not in v:
            logger.info("OpenAI API key is configured")
            return v.strip()
        return ""
    
    @field_validator("OPENAIORG_ID")
    @classmethod
    def validate_openai_org_id(cls, v):
        """Validate OpenAI organization ID is properly set."""
        if v is None:
            return None
        
        if not v.strip() or "dummy" in v:
            logger.info("No valid OpenAI organization ID provided, will use API key without organization")
            return None
        
        logger.info("OpenAI organization ID is configured")
        return v.strip()
    
    @field_validator("TWILIO_API_KEY")
    @classmethod
    def validate_twilio_key(cls, v):
        """Validate Twilio API key is properly set."""
        if v and v.strip() and "dummy" not in v:
            logger.info("Twilio API key is configured")
            return v.strip()
        return ""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }

@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance.
    
    Using lru_cache to avoid reloading settings on every request.
    """
    return Settings()

settings = get_settings()

def get_openai_client_params():
    """
    Get parameters for OpenAI client initialization.
    
    Returns:
        dict: Parameters for OpenAI client
    """
    params = {"api_key": settings.OPENAI_API_KEY}
    
    if settings.OPENAIORG_ID is not None:
        params["organization"] = settings.OPENAIORG_ID

    print(f"OpenAI client parameters: {params}")
        
    return params

if __name__ == "__main__":
    # print("\nEnvironment variable values:")
    # print(f"OPENAI_API_KEY from env: {os.getenv('OPENAI_API_KEY', 'Not found')}")
    # print(f"OPENAI_ORG_ID from env: {os.getenv('OPENAI_ORG_ID', 'Not found')}")
    
    # print("\nSettings values:")
    # print(f"OpenAI API Key: {'Configured' if settings.OPENAI_API_KEY else 'Not configured'}")
    # print(f"OpenAI Org ID: {'Configured as: ' + settings.OPENAI_ORG_ID if settings.OPENAI_ORG_ID else 'Not configured'}")
    # print(f"Twilio API Key: {'Configured' if settings.TWILIO_API_KEY else 'Not configured'}")
    # print(f"Twilio API Secret: {'Configured' if settings.TWILIO_API_SECRET else 'Not configured'}")
    
    # print("\nOpenAI client parameters:")
    print(get_openai_client_params())