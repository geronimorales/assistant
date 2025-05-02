from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    LLM_MODEL: str
    LLM_PROVIDER: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
