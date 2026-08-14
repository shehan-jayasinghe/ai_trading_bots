from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import websockets

from app.candle import MultiTimeframeCandleBuilder
from app.kafka import KafkaPublisher
from app.settings import Settings

logger = logging.getLogger(__name__)


class DerivProducerWorker:
    """Build Deriv gold candles (1s / 1m / 2m / 3m / …) and publish to Kafka only."""

    name = "deriv"

    def __init__(self, settings: Settings, kafka: KafkaPublisher) -> None:
        self._settings = settings
        self._kafka = kafka
        self._stop = asyncio.Event()
        self._req_id = 1
        self._status: dict[str, Any] = {
            "name": self.name,
            "running": False,
            "last_error": None,
            "candles_published": 0,
            "authorized": False,
        }
        self._builder = MultiTimeframeCandleBuilder(
            timeframes=settings.deriv_tf_list,
            entity="gold",
            source="deriv",
            symbol=settings.deriv_symbol,
        )

    @property
    def status(self) -> dict[str, Any]:
        return dict(self._status)

    def request_stop(self) -> None:
        self._stop.set()

    def _next_req_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def run(self) -> None:
        if not self._settings.deriv_token.strip():
            self._status["last_error"] = "DERIV_TOKEN is empty"
            logger.error("deriv worker not started: DERIV_TOKEN missing")
            return

        self._status["running"] = True
        self._status["last_error"] = None
        logger.info(
            "deriv worker start symbol=%s tfs=%s",
            self._settings.deriv_symbol,
            self._settings.deriv_tf_list,
        )
        try:
            while not self._stop.is_set():
                try:
                    await self._session_loop()
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self._status["last_error"] = str(exc)
                    self._status["authorized"] = False
                    logger.warning("deriv session error: %s; reconnect in 3s", exc)
                    await asyncio.sleep(3)
        finally:
            self._status["running"] = False
            self._status["authorized"] = False

    async def _session_loop(self) -> None:
        url = f"{self._settings.deriv_ws_endpoint}?app_id={self._settings.deriv_app_id}"
        async with websockets.connect(url, ping_interval=20) as ws:
            auth_id = self._next_req_id()
            await ws.send(
                json.dumps({"authorize": self._settings.deriv_token, "req_id": auth_id})
            )
            auth_msg = await self._wait_req_id(ws, auth_id)
            if auth_msg.get("error"):
                raise RuntimeError(f"Deriv authorize failed: {auth_msg['error']}")
            self._status["authorized"] = True
            logger.info("deriv authorized app_id=%s", self._settings.deriv_app_id)

            # Deriv API name is "ticks"; we only use quotes to build candles.
            sub_id = self._next_req_id()
            await ws.send(
                json.dumps(
                    {
                        "ticks": self._settings.deriv_symbol,
                        "subscribe": 1,
                        "req_id": sub_id,
                    }
                )
            )
            sub_msg = await self._wait_req_id(ws, sub_id)
            if sub_msg.get("error"):
                raise RuntimeError(f"Deriv quote subscribe failed: {sub_msg['error']}")
            logger.info("deriv quote stream subscribed symbol=%s", self._settings.deriv_symbol)

            while not self._stop.is_set():
                raw = await asyncio.wait_for(ws.recv(), timeout=60)
                msg = json.loads(raw)
                if msg.get("error"):
                    raise RuntimeError(f"Deriv stream error: {msg['error']}")
                quote = msg.get("tick")
                if not quote:
                    continue
                await self._handle_quote(quote)

    async def _wait_req_id(
        self,
        ws: websockets.ClientConnection,
        req_id: int,
        timeout_sec: float = 30.0,
    ) -> dict[str, Any]:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_sec
        while loop.time() < deadline:
            raw = await asyncio.wait_for(ws.recv(), timeout=timeout_sec)
            data = json.loads(raw)
            if data.get("req_id") == req_id:
                return data
        raise TimeoutError(f"Deriv timeout waiting for req_id={req_id}")

    async def _handle_quote(self, quote: dict[str, Any]) -> None:
        price = float(quote["quote"])
        epoch = int(quote["epoch"])
        event_time_ms = epoch * 1000
        # Deriv FX has no true volume; count each quote update as volume 1
        qty = 1.0

        closed = self._builder.on_price(price=price, qty=qty, event_time_ms=event_time_ms)
        for candle in closed:
            await self._kafka.publish(self._settings.kafka_topic_candles_gold, candle)
            self._status["candles_published"] += 1
