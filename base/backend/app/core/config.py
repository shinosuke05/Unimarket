"""Đọc cấu hình từ file .env hoặc biến môi trường."""

from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "UniMarket API"

    # Database
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "app_db"

    # CORS
    CORS_ORIGINS: str = "*"

    # Admin
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = "System Admin"

    # JWT
    SECRET_KEY: str
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Upload ảnh
    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_MB: int = 2
    MAX_IMAGES_PER_ITEM: int = 5

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:"
            f"{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def upload_path(self) -> Path:
        return Path(__file__).resolve().parents[2] / self.UPLOAD_DIR


settings = Settings()