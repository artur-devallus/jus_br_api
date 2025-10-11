from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    LOG_LEVEL: str = "INFO"

    TWO_CAPTCHA_KEY: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings() # noqa