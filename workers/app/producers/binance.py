from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import httpx
import websockets

from app.candle import MultiTimeframeCandleBuilder
from app.kafka import KafkaPublisher
from app.schemas import MarketEnvelope
from app.settings import Settings

logger = logging.getLogger(__name__)


class BinanceProducerWorker:
    """Build Binance BTC candles (1s / 2s / 1m / …) and publish to Kafka only."""

    name = "binance"

    def __init__(self, settings: Settings, kafka: KafkaPublisher) -> None:
        self._settings = settings
        self._kafka = kafka
        self._stop = asyncio.Event()
        self._status: dict[str, Any] = {
            "name": self.name,
            "running": False,
            "last_error": None,
            "candles_published": 0,
        }
        self._builder = MultiTimeframeCandleBuilder(
            timeframes=settings.binance_tf_list,
            entity="btc",
            source="binance",
            symbol=settings.binance_symbol.upper(),
        )

    @property
    def status(self) -> dict[str, Any]:
        return dict(self._status)

    async def run(self) -> None:
        self._status["running"] = True
        self._status["last_error"] = None
        logger.info(
            "binance worker start symbol=%s tfs=%s",
            self._settings.binance_symbol,
            self._settings.binance_tf_list,
        )
        try:
            while not self._stop.is_set():
                try:
                    await asyncio.gather(
                        self._trade_stream_loop(),
                        self._kline_poll_loop(),
                    )
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self._status["last_error"] = str(exc)
                    logger.warning("binance worker error: %s; restart in 5s", exc)
                    await asyncio.sleep(5)
        finally:
            self._status["running"] = False

    def request_stop(self) -> None:
        self._stop.set()

    async def _trade_stream_loop(self) -> None:
        """Use trade stream only to assemble candles; never publish raw trades."""
        symbol = self._settings.binance_symbol.lower()
        url = f"{self._settings.binance_ws_url}/{symbol}@trade"
        while not self._stop.is_set():
            try:
                async with websockets.connect(url, ping_interval=20) as ws:
                    logger.info("binance trade ws connected %s", url)
                    while not self._stop.is_set():
                        raw = await asyncio.wait_for(ws.recv(), timeout=60)
                        msg = json.loads(raw)
                        await self._handle_trade(msg)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._status["last_error"] = str(exc)
                logger.warning("binance trade ws error: %s; reconnect in 3s", exc)
                await asyncio.sleep(3)

    async def _handle_trade(self, msg: dict[str, Any]) -> None:
        price = float(msg["p"])
        qty = float(msg["q"])
        event_time_ms = int(msg.get("T") or msg.get("E") or 0)
        if event_time_ms <= 0:
            return

        closed = self._builder.on_price(price=price, qty=qty, event_time_ms=event_time_ms)
        for candle in closed:
            await self._kafka.publish(self._settings.kafka_topic_candles_btc, candle)
            self._status["candles_published"] += 1

    async def _kline_poll_loop(self) -> None:
        """Also poll native 1m klines when 1m is configured (authoritative close)."""
        if "1m" not in self._settings.binance_tf_list:
            await self._stop.wait()
            return

        symbol = self._settings.binance_symbol.upper()
        url = f"{self._settings.binance_base_url}/api/v3/klines"
        last_closed_open_ms: int | None = None

        async with httpx.AsyncClient(timeout=30.0) as client:
            while not self._stop.is_set():
                try:
                    resp = await client.get(
                        url,
                        params={"symbol": symbol, "interval": "1m", "limit": 2},
                    )
                    resp.raise_for_status()
                    rows = resp.json()
                    if len(rows) >= 2:
                        closed = rows[-2]
                        open_ms = int(closed[0])
                        if last_closed_open_ms != open_ms:
                            last_closed_open_ms = open_ms
                            envelope = MarketEnvelope(
                                entity="btc",
                                source="binance",
                                symbol=symbol,
                                timeframe="1m",
                                bucket_epoch=open_ms // 1000,
                                event_time_ms=int(closed[6]),
                                payload={
                                    "open": float(closed[1]),
                                    "high": float(closed[2]),
                                    "low": float(closed[3]),
                                    "close": float(closed[4]),
                                    "volume": float(closed[5]),
                                    "trade_count": int(closed[8]),
                                    "source_interval": "binance_kline_1m",
                                },
                            )
                            await self._kafka.publish(
                                self._settings.kafka_topic_candles_btc,
                                envelope,
                            )
                            self._status["candles_published"] += 1
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self._status["last_error"] = str(exc)
                    logger.warning("binance kline poll error: %s", exc)

                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=15.0)
                except asyncio.TimeoutError:
                    pass
