from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env") if (PROJECT_ROOT / ".env").exists() else None,
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "Insique"
    project_name: str = "Insique"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(min_length=16)
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    database_url: str
    jwt_algorithm: str = "HS256"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    market_data_cache_days: int = 7
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 60
    resend_api_key: str = ""
    from_email: str = ""
    frontend_url: str = "http://localhost:3000"
    password_reset_expire_minutes: int = 15
    forgot_password_rate_limit_attempts: int = 5
    forgot_password_rate_limit_window_minutes: int = 15
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    @field_validator("database_url")
    @classmethod
    def ensure_psycopg_driver(cls, v: str) -> str:
        if v and v.startswith("postgresql://") and "+" not in v.split("://")[0]:
            v = v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v



@lru_cache
def get_settings() -> Settings:
    return Settings()
