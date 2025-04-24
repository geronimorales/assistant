import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Singleton class for managing environment variables."""
    
    # Database settings
    DATABASE_URL: str = Field(
        ...,
        description="Database connection URL",
        example="postgresql+asyncpg://user:password@localhost:5432/dbname"
    )
    
    # LLM settings
    LLM_MODEL: str = Field(
        ...,
        description="LLM model to use",
        example="gpt-4"
    )
    LLM_PROVIDER: str = Field(
        ...,
        description="LLM provider (openai or ollama)",
        example="openai"
    )
    OPENAI_API_KEY: str = Field(
        ...,
        description="OpenAI API key",
        example="sk-..."
    )
    
    # Optional settings with defaults
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # API settings
    API_PREFIX: str = Field(
        default="/api/v1",
        description="API prefix"
    )
    API_TITLE: str = Field(
        default="AI Assistant API",
        description="API title"
    )
    API_VERSION: str = Field(
        default="0.1.0",
        description="API version"
    )
    
    # CORS settings
    CORS_ORIGINS: list[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    CORS_METHODS: list[str] = Field(
        default=["*"],
        description="CORS allowed methods"
    )
    CORS_HEADERS: list[str] = Field(
        default=["*"],
        description="CORS allowed headers"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider."""
        allowed_providers = ["openai", "ollama"]
        if v.lower() not in allowed_providers:
            raise ValueError(f"LLM_PROVIDER must be one of {allowed_providers}")
        return v.lower()
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        allowed_environments = ["development", "staging", "production"]
        if v.lower() not in allowed_environments:
            raise ValueError(f"ENVIRONMENT must be one of {allowed_environments}")
        return v.lower()
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v.upper()
    
    @classmethod
    def get_instance(cls) -> "Settings":
        """Get the singleton instance of Settings."""
        if not hasattr(cls, "_instance"):
            # Ensure .env file exists
            env_path = Path(".env")
            if not env_path.exists():
                raise FileNotFoundError(
                    ".env file not found. Please create one based on .env.example"
                )
            cls._instance = cls()
        return cls._instance
    
    def __new__(cls) -> "Settings":
        """Ensure only one instance of Settings exists."""
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance


# Create a global settings instance
settings = Settings.get_instance() 