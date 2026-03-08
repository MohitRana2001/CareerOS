from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "resume-tailor-api"
    env: str = "dev"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/resume_tailor"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    google_client_id: str = ""
    gemini_api_key: str = ""
    gemini_default_model: str = "gemini-2.5-pro"
    storage_public_base_url: str = "https://storage.example.com/careeros"
    drive_share_base_url: str = "https://drive.google.com/file/d"
    allow_dev_auth_header: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
