import os
import json
from dotenv import load_dotenv

from typing import Any, Dict

load_dotenv()


class AppConfig:
    """Configuration manager that reads from environment variables."""

    _instance = None
    _initialized = False
    _config: Dict[str, Any] = {
        "app": {
            "env": os.getenv("APP_ENV", "local"),
            "debug": os.getenv("APP_DEBUG", "false").lower() == "true",
            "log_level": os.getenv("APP_LOG_LEVEL", "INFO"),
            "testing": os.getenv("APP_TESTING", "false").lower() == "true",
        },
        "database": {
            "url": os.getenv(
                "DATABASE_URL",
                "postgresql+asyncpg://postgres:postgres@localhost:5432/assistant",
            ),
            "test_url": os.getenv(
                "DATABASE_TEST_URL",
                "postgresql+asyncpg://postgres:postgres@localhost:5432/assistant_test",
            ),
            "log_print": os.getenv("DATABASE_LOG_PRINT", "false").lower() == "true",
        },
        "llm": {
            "max_tokens": os.getenv("LLM_MAX_TOKENS"),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "provider": os.getenv("LLM_PROVIDER", "ollama"),
            "system_prompt": os.getenv("LLM_SYSTEM_PROMPT", "DEFAULT_SYSTEM_PROMPT"),
            "memory": {
                "async_database_url": os.getenv("LLM_MEMORY_ASYNC_DATABASE_URL", None)
            },
            "mcp": {
                "servers": os.getenv("LLM_MCP_SERVERS", "").split(","),
            },
            "openai": {
                "api_key": os.getenv("LLM_OPENAI_API_KEY"),
                "model": os.getenv("LLM_OPENAI_MODEL", "gpt-4o-mini"),
                "temperature": float(os.getenv("LLM_OPENAI_TEMPERATURE", "0.7")),
                "max_tokens": os.getenv("LLM_OPENAI_MAX_TOKENS"),
                "embedding_model": os.getenv(
                    "LLM_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
                ),
                "embedding_dimension": int(
                    os.getenv("LLM_OPENAI_EMBEDDING_DIMENSION", "768")
                ),
            },
            "ollama": {
                "host": os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"),
                "request_timeout": float(os.getenv("OLLAMA_REQUEST_TIMEOUT", "120.0")),
                "model": os.getenv("LLM_OLLAMA_MODEL", "llama3.2:8b"),
                "temperature": float(os.getenv("LLM_OLLAMA_TEMPERATURE", "0.7")),
                "max_tokens": os.getenv("LLM_OLLAMA_MAX_TOKENS"),
                "embedding_model": os.getenv(
                    "LLM_OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"
                ),
                "embedding_dimension": int(
                    os.getenv("LLM_OLLAMA_EMBEDDING_DIMENSION", "768")
                ),
            },
        },
        "llamaindex": {
            "data_dir": os.getenv("LLAMA_INDEX_DATA_DIR", "data"),
            "data_table": os.getenv("LLAMA_INDEX_DATA_TABLE", "embeddings"),
        },
        "api": {
            "prefix": os.getenv("API_PREFIX", "/api/v1"),
            "title": os.getenv("API_TITLE", "AI Assistant API"),
            "version": os.getenv("API_VERSION", "0.1.0"),
        },
        "cors": {
            "origins": os.getenv("CORS_ORIGINS", '["*"]'),
            "methods": os.getenv("CORS_METHODS", '["*"]'),
            "headers": os.getenv("CORS_HEADERS", '["*"]'),
        },
    }

    def __new__(cls) -> "AppConfig":
        """Ensure only one instance of AppConfig exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration."""
        if not self._initialized:
            self._validate_config()
            self._initialized = True

    def _validate_config(self) -> None:
        """Validate the configuration values."""
        # Validate LLM provider
        if self._config["llm"]["provider"] not in ["openai", "ollama"]:
            raise ValueError(f"Invalid LLM provider: {self._config['llm']['provider']}")

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self._config["app"]["log_level"].upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self._config['app']['log_level']}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: The configuration key in dot notation (e.g., "app.env")
            default: Default value to return if key is not found

        Returns:
            The configuration value or default if not found
        """
        if not self._initialized:
            self.__init__()

        try:
            value = self._config
            for k in key.split("."):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @classmethod
    def get_instance(cls) -> "AppConfig":
        """Get the singleton instance of AppConfig."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Create a global configuration instance
config = AppConfig.get_instance()
