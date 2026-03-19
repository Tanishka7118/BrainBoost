import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "BrainBoost Study Analyzer"
    app_version: str = "1.0.0"
    secret_key: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./brainboost.db")
    hf_api_token: str | None = os.getenv("HF_API_TOKEN")
    hf_model: str = os.getenv("HF_MODEL", "HuggingFaceH4/zephyr-7b-beta")


settings = Settings()
