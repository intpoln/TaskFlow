from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"] = "PROD"

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    @property
    def REDIS_URI(self):
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URI(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REFRESH_TOKEN_COOKIE_MAX_AGE: int

    SUPERUSER_EMAIL: str
    SUPERUSER_USERNAME: str
    SUPERUSER_PASSWORD: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    GOOGLE_OAUTH_GET_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    GOOGLE_OAUTH_AUTHORIZE_URI: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_JWK_URI: str = "https://www.googleapis.com/oauth2/v3/certs"
    GOOGLE_ISSUER: str = "https://accounts.google.com"
    GOOGLE_CALLBACK_URI: str = "http://localhost:8000/oauth/google/callback"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
