from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from app.pool import ProducerWorkerPool
from app.settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    pool = ProducerWorkerPool(settings)
    app.state.pool = pool
    app.state.settings = settings
    await pool.start()
    logger.info("ingest API ready on %s:%s", settings.host, settings.port)
    try:
        yield
    finally:
        await pool.stop()


app = FastAPI(
    title="Ingest producers",
    description="FastAPI worker pool: Binance BTC + Deriv gold candles → Kafka",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict:
    pool: ProducerWorkerPool = app.state.pool
    return {"ok": True, "pool": pool.status()}


@app.get("/workers")
async def workers() -> dict:
    pool: ProducerWorkerPool = app.state.pool
    return pool.status()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()
