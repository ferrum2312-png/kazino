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

    # TON payments / deposits -> Stars
    ton_deposit_address: str = "UQAyMFJX-kJF44Em2HVHq6gjTWKOIGXKTEDL6AMJ6JqNEfXA"
    ton_api_base: str = "https://tonapi.io"
    ton_api_key: str = ""            # optional TonAPI key (tonconsole.com) for higher limits
    star_usd_price: float = 0.015    # 50 Stars = $0.75 -> $0.015 per Star
    # GRAM (ex-TON) USD price is parsed & averaged from these exchanges:
    kucoin_symbol: str = "GRAM-USDT"
    bybit_symbol: str = "GRAMUSDT"
    rate_cache_seconds: int = 120    # how long to cache the GRAM/USD price
    deposit_poll_seconds: int = 20   # how often the watcher polls for new deposits
    deposits_enabled: bool = True    # master switch for the on-chain deposit watcher

    # Public base URL (for the Telegram bot webhook).
    public_base_url: str = "https://titorovka.icu"

    # Crypto Pay (@CryptoBot) — token from env only (repo is public!).
    crypto_pay_token: str = ""
    crypto_pay_base: str = "https://pay.crypt.bot"  # mainnet; testnet: https://testnet-pay.crypt.bot
    crypto_pay_poll_seconds: int = 15

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
