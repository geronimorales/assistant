from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None
    LLM_MEMORY_ASYNC_DATABASE_URL: str | None = None

    # LLM settings
    LLM_MODEL: str | None = None
    LLM_PROVIDER: str = "ollama"  # Default to ollama
    LLM_SYSTEM_PROMPT: str | None = None
    LLM_OLLAMA_MODEL: str | None = None
    LLM_MCP_SERVERS: str | None = None
    LLM_OLLAMA_EMBEDDING_MODEL: str | None = None
    LLM_OLLAMA_EMBEDDING_DIMENSION: str | None = None

    # OpenAI settings
    OPENAI_API_KEY: str | None = None

    # LlamaIndex settings
    LLAMA_INDEX_DATA_TABLE: str | None = None
    LLAMA_INDEX_DATA_DIR: str | None = None

    # Ollama settings
    OLLAMA_HOST: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
