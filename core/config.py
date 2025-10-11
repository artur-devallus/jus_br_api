from pydantic.env_settings import BaseSettings, AnyUrl


class Settings(BaseSettings):
    DATABASE_URL: AnyUrl

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
