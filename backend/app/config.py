from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str = "set-me-in-dot-env"
    groq_model: str = "openai/gpt-oss-120b"
    groq_model_fast: str = "openai/gpt-oss-20b"
    app_env: str = "development"
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:8501"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
