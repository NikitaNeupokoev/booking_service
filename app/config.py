from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):
    """Конфигурация и настройки приложения."""

    APP_NAME: str = 'Booking Service'
    DEBUG: bool = False

    DATABASE_URL: str = (
        'postgresql+asyncpg://postgres:postgres@db:5432/booking_db'
    )

    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings()
