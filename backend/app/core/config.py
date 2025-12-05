from dotenv import load_dotenv

import os

from pydantic.v1 import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    SECRET_AUTH: str = os.environ.get("SECRET_AUTH")

    DB_USER: str = os.environ.get("DB_USER")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.environ.get("DB_PORT")
    DB_NAME: str = os.environ.get("DB_NAME")

    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SYNC_DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    CELERY_BROKER_URL: str = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND: str = os.environ.get('CELERY_RESULT_BACKEND')

    EMAIL_HOST_USER: str = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD: str = os.getenv('EMAIL_HOST_PASSWORD')

    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY')

    REDIS_URL: str = os.getenv('REDIS_URL')

    class Config:
        env_file = ".env"


settings = Settings()
