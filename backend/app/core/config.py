import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base directory for the backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "DarGlobal & Wasalt Real Estate Intelligence"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # LLM Settings
    LLM_PROVIDER: str = Field(default="gemini", description="LLM provider: 'gemini' or 'openrouter'")
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", description="Gemini model name")
    
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API Key")
    OPENROUTER_MODEL: str = Field(
        default="meta-llama/llama-3.3-70b-instruct:free",
        description="OpenRouter model name"
    )

    # Embedding and RAG Settings
    EMBEDDING_MODEL_NAME: str = Field(default="all-MiniLM-L6-v2", description="Embedding model name")
    CHROMA_PERSIST_DIR: str = Field(
        default=str(BASE_DIR / "data" / "vector_db"),
        description="ChromaDB persistence directory"
    )
    CHROMA_COLLECTION_NAME: str = "real_estate_knowledge"
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.35
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120

    # Storage Paths
    SQLITE_DB_PATH: str = Field(
        default=str(BASE_DIR / "data" / "app_metadata.db"),
        description="SQLite database path"
    )
    RAW_DATA_DIR: str = Field(
        default=str(BASE_DIR / "data" / "raw"),
        description="Directory for raw scraped data"
    )
    PROCESSED_DATA_DIR: str = Field(
        default=str(BASE_DIR / "data" / "processed"),
        description="Directory for processed data"
    )

    # Security & Admin
    ADMIN_SECRET_KEY: str = Field(default="darglobal-admin-secret-2026", description="Admin endpoint secret key")
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]


settings = Settings()
