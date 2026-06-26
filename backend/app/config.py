from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
INDEX_DIR = STORAGE_DIR / "indexes"
PROMPTS_DIR = BASE_DIR / "prompts"

PDF_MAGIC = b"%PDF"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 250
    top_k: int = 6
    retrieval_fetch_k: int = 15
    similarity_threshold: float = 1.25
    heading_match_threshold_margin: float = 0.25
    max_upload_mb: int = 25
    summary_max_chars: int = 12000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    port: int = 8000

    @field_validator("openai_api_key")
    @classmethod
    def strip_api_key(cls, value: str) -> str:
        return value.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)


def load_prompt(name: str) -> tuple[str, str]:
    content = (PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")
    system_part, user_part = content.split("===USER===", 1)
    system = system_part.replace("===SYSTEM===", "").strip()
    return system, user_part.strip()


def find_upload(document_id: str) -> Path | None:
    matches = list(UPLOAD_DIR.glob(f"{document_id}_*"))
    return matches[0] if matches else None
