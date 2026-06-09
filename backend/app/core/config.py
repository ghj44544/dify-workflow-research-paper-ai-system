from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="科研文献智能分析系统", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")

    database_url: str = Field(
        default="mysql+pymysql://root:password@localhost:3306/paper_ai_system?charset=utf8mb4",
        alias="DATABASE_URL",
    )

    dify_base_url: str = Field(default="http://localhost/v1", alias="DIFY_BASE_URL")
    dify_qa_api_key: str = Field(default="", alias="DIFY_QA_API_KEY")
    dify_extract_api_key: str = Field(default="", alias="DIFY_EXTRACT_API_KEY")
    dify_note_api_key: str = Field(default="", alias="DIFY_NOTE_API_KEY")

    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
