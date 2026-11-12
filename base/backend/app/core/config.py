from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "UniMarket API"

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "app_db"

    CORS_ORIGINS: str = "*"

    JWT_SECRET_KEY: str = ""
    JWT_EXPIRE_MINUTES: int = 60

    @property
    def database_url(self):
        return (
            f"mysql+pymysql://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def cors_origin_list(self):
        return self.CORS_ORIGINS.split(",")

    class Config:
        env_file = ".env"


settings = Settings()
