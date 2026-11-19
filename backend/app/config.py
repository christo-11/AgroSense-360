from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    database_url: SecretStr = SecretStr("")
    jwt_secret: SecretStr = SecretStr("")
    frontend_origins: str = "http://localhost:5173"
    sentinel_hub_client_id: str = ""
    sentinel_hub_client_secret: str = ""
    agmarknet_api_key: str = ""
    agricultural_admin_emails: str = ""
    public_demo_mode: bool = False
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
        case_sensitive=False,
        hide_input_in_errors=True,
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        raw_url = value.get_secret_value()
        if raw_url:
            try:
                parsed_url = make_url(raw_url)
            except ArgumentError:
                raise ValueError("DATABASE_URL must be a valid PostgreSQL or SQLite URL.") from None
            if parsed_url.drivername not in {"postgresql+psycopg", "sqlite", "sqlite+pysqlite"}:
                raise ValueError("DATABASE_URL must use postgresql+psycopg or sqlite.")
            if parsed_url.drivername == "postgresql+psycopg" and not parsed_url.host:
                raise ValueError("DATABASE_URL must include a PostgreSQL host.")
        return value

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if secret and (len(secret) < 32 or secret.lower().startswith("replace-with-")):
            raise ValueError("JWT_SECRET must be a non-placeholder secret of at least 32 characters.")
        return value

    @field_validator("frontend_origins")
    @classmethod
    def validate_frontend_origins(cls, value: str) -> str:
        origins = [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
        if not origins or "*" in origins:
            raise ValueError("FRONTEND_ORIGINS must contain explicit HTTP(S) origins and cannot use '*'.")
        for origin in origins:
            try:
                parsed = urlsplit(origin)
                port = parsed.port
            except ValueError:
                raise ValueError("FRONTEND_ORIGINS contains an invalid origin.") from None
            if (
                "*" in origin
                or parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.username is not None
                or parsed.password is not None
                or (port is not None and port == 0)
                or parsed.path
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("FRONTEND_ORIGINS entries must be HTTP(S) origins without paths.")
        return ",".join(origins)

    @property
    def database_url_value(self) -> str:
        return self.database_url.get_secret_value()

    @property
    def jwt_secret_value(self) -> str:
        return self.jwt_secret.get_secret_value()

    @property
    def auth_configured(self) -> bool:
        return len(self.jwt_secret_value) >= 32

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @property
    def agricultural_admin_email_set(self) -> frozenset[str]:
        return frozenset(
            email.strip().casefold()
            for email in self.agricultural_admin_emails.split(",")
            if email.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
