import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Hermes Agent OS Core"
    APP_ENV: str = "local"  # local, development, production
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database Configuration (local, postgres, firebase)
    DB_MODE: str = "local"  # "local" (SQLite), "postgres", or "firebase" (Firestore)
    SQLITE_URL: str = "sqlite:///./agent_os_local.db"
    POSTGRES_URL: str = "postgresql://postgres:postgres@localhost:5432/agent_os"
    
    # Firebase settings (optional, used if DB_MODE == "firebase")
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None

    # Vector DB (ChromaDB) Configuration
    CHROMA_PERSIST_DIR: str = "./data/chromadb"
    VECTOR_DB_COLLECTION: str = "agent_os_semantic_memory"

    # AI Inference & Orchestration
    OLLAMA_URL: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "gemma:2b"  # Default local model family

    # Sandboxing & Code Execution
    SANDBOX_WORK_DIR: str = "./data/sandbox"
    SANDBOX_TIMEOUT_SEC: int = 30
    MAX_MEMORY_LIMIT_MB: int = 512

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
os.makedirs(os.path.dirname(settings.SQLITE_URL.replace("sqlite:///", "")), exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.SANDBOX_WORK_DIR, exist_ok=True)
