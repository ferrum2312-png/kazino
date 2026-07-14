import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_models
from app.routers import (
    auth,
    catalog,
    crash,
    crypto_webhook,
    mines,
    payments,
    telegram_webhook,
    users,
)
from app.services import telegram_bot
from app.services.crash_engine import engine
from app.services.crypto_pay_watcher import watcher as crypto_watcher
from app.services.deposit_watcher import watcher as deposit_watcher
from app.services.redis_client import close_redis


_DEFAULT_SECRET = "change-me-in-production-super-secret-key"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if settings.environment != "development" and settings.secret_key == _DEFAULT_SECRET:
        print(
            "[SECURITY] WARNING: SECRET_KEY is the default value — JWTs and the "
            "Telegram webhook secret are forgeable. Set a strong SECRET_KEY!"
        )
    await init_models()
    try:
        await telegram_bot.set_webhook()  # for Stars payment updates
    except Exception as exc:
        print(f"[bot] set_webhook failed: {exc}")
    crash_task = asyncio.create_task(engine.run_forever())
    deposit_task = asyncio.create_task(deposit_watcher.run_forever())
    crypto_task = asyncio.create_task(crypto_watcher.run_forever())
    yield
    # Shutdown
    engine.stop()
    deposit_watcher.stop()
    crypto_watcher.stop()
    for task in (crash_task, deposit_task, crypto_task):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    await close_redis()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = settings.api_prefix
app.include_router(auth.router, prefix=api)
app.include_router(users.router, prefix=api)
app.include_router(catalog.router, prefix=api)
app.include_router(mines.router, prefix=api)
app.include_router(crash.router, prefix=api)
app.include_router(payments.router, prefix=api)
app.include_router(telegram_webhook.router, prefix=api)
app.include_router(crypto_webhook.router, prefix=api)


@app.get("/")
async def root():
    return {"name": settings.app_name, "status": "ok", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
