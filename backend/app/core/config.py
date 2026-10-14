from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Support Hub"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+psycopg://ai_support:ai_support_dev@postgres:5432/ai_support_hub"
    )
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    llm_mock_mode: bool = True
    chunk_size: int = Field(1000, ge=200, le=8000)
    chunk_overlap: int = Field(150, ge=0, le=2000)
    top_k: int = Field(5, ge=1, le=20)
    min_relevance_score: float = Field(0.35, ge=0, le=1)
    max_upload_mb: int = Field(15, ge=1, le=100)
    cors_origins: str = "http://localhost:3000"
    n8n_base_url: str = "http://n8n:5678"
    n8n_webhook_url: str = "http://n8n:5678/webhook/knowledge-indexed"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
