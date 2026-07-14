import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_models
from app.routers import auth, catalog, crash, mines, payments, users
from app.services.crash_engine import engine
from app.services.deposit_watcher import watcher
from app.services.redis_client import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_models()
    crash_task = asyncio.create_task(engine.run_forever())
    deposit_task = asyncio.create_task(watcher.run_forever())
    yield
    # Shutdown
    engine.stop()
    watcher.stop()
    for task in (crash_task, deposit_task):
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


@app.get("/")
async def root():
    return {"name": settings.app_name, "status": "ok", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
