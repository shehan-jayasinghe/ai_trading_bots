from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.kafka import KafkaPublisher
from app.producers.binance import BinanceProducerWorker
from app.producers.deriv import DerivProducerWorker
from app.settings import Settings

logger = logging.getLogger(__name__)


class ProducerWorkerPool:
    """FastAPI-managed pool that runs market producers as background tasks."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._kafka = KafkaPublisher(settings)
        self._workers: list[Any] = []
        self._tasks: list[asyncio.Task[None]] = []
        self._started = False

    @property
    def started(self) -> bool:
        return self._started

    async def start(self) -> None:
        if self._started:
            return
        await self._kafka.start()

        if self._settings.worker_enable_binance:
            self._workers.append(BinanceProducerWorker(self._settings, self._kafka))
        if self._settings.worker_enable_deriv:
            self._workers.append(DerivProducerWorker(self._settings, self._kafka))

        for worker in self._workers:
            task = asyncio.create_task(self._run_worker(worker), name=f"worker:{worker.name}")
            self._tasks.append(task)

        self._started = True
        logger.info(
            "worker pool started count=%s names=%s",
            len(self._workers),
            [w.name for w in self._workers],
        )

    async def stop(self) -> None:
        for worker in self._workers:
            worker.request_stop()
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        self._workers.clear()
        await self._kafka.stop()
        self._started = False
        logger.info("worker pool stopped")

    def status(self) -> dict[str, Any]:
        return {
            "started": self._started,
            "workers": [w.status for w in self._workers],
        }

    async def _run_worker(self, worker: Any) -> None:
        while not worker._stop.is_set():
            try:
                await worker.run()
                # Clean exit (disabled / missing config) — do not restart forever
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.exception("worker %s failed: %s; restart in 5s", worker.name, exc)
                await asyncio.sleep(5)
