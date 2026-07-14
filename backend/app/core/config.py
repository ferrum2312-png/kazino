from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Kazino API"
    environment: str = "development"
    api_prefix: str = "/api"

    # Security
    secret_key: str = "change-me-in-production-super-secret-key"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    algorithm: str = "HS256"

    # Database
    database_url: str = (
        "postgresql+asyncpg://kazino:kazino@localhost:5432/kazino"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Telegram Mini App
    bot_token: str = ""              # from @BotFather; required for Telegram login
    telegram_auth_max_age: int = 86400  # reject initData older than this (seconds); 0 disables

    # Gameplay
    starting_balance: float = 1000.0
    crash_house_edge: float = 0.03  # 3%
    crash_bet_seconds: int = 6      # betting window duration
    crash_tick_ms: int = 100        # multiplier tick interval

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
