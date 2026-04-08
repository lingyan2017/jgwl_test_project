from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "JGWL 管理系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DB_HOST: str = "123.56.164.133"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "1qaz3edc"
    DB_NAME: str = "jgwl_db"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    SECRET_KEY: str = "jgwl-secret-key-2024-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    class Config:
        env_file = ".env"


settings = Settings()
