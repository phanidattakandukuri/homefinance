from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HomeFin AI API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_secret_key: SecretStr = SecretStr("development-only-change-me")
    database_url: str = Field(
        default="postgresql+psycopg://homefin:change-me@localhost:5432/homefin",
        description="SQLAlchemy URL for the application database.",
    )
    jwt_secret_key: SecretStr = SecretStr("development-only-change-me")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"])
    upload_dir: str = "./private_uploads"
    max_upload_size_mb: int = 15
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-2.0-flash"

    @model_validator(mode="after")
    def production_secrets(self):
        if self.app_env == "production":
            if not self.app_secret_key.get_secret_value() or self.app_secret_key.get_secret_value().startswith("development-"):
                raise ValueError("APP_SECRET_KEY must be configured in production")
            if not self.jwt_secret_key.get_secret_value() or self.jwt_secret_key.get_secret_value().startswith("development-"):
                raise ValueError("JWT_SECRET_KEY must be configured in production")
        return self

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
