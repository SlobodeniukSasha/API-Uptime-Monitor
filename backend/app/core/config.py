from dotenv import load_dotenv

import os

from pydantic.v1 import BaseSettings

load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

SECRET_AUTH = os.environ.get("SECRET_AUTH")

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

REDIS_URL = os.getenv('REDIS_URL')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


class Settings(BaseSettings):
    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SYNC_DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    CELERY_BROKER_URL: str = CELERY_BROKER_URL
    CELERY_RESULT_BACKEND: str = CELERY_RESULT_BACKEND

    EMAIL_HOST_USER: str = EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD: str = EMAIL_HOST_PASSWORD

    GEMINI_API_KEY: str = GEMINI_API_KEY

    REDIS_URL: str = REDIS_URL

    class Config:
        env_file = ".env"


settings = Settings()
