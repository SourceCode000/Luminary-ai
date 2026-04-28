from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    secret_key: str
    openai_api_key: str
    database_url: str
    access_token_expire_minutes: int = 30 

    # Redis
    redis_url: str = "redis://localhost:6379"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # AI Settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    rag_top_k: int = 5
    llm_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    # Auth
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 60

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()