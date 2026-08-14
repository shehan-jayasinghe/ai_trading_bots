from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import websockets

from app.flow import FlowCalculator
from app.kafka import KafkaPublisher
from app.settings import Settings

logger = logging.getLogger(__name__)


def _trade_side(is_buyer_maker: bool) -> str:
    # m=true → buyer is maker → seller is taker → aggressive SELL
    return "SELL" if is_buyer_maker else "BUY"


class BinanceFlowWorker:
    """Binance trades + depth → Kafka materials (market-trades / market-orderbook / market-flow)."""

    name = "binance-flow"

    def __init__(self, settings: Settings, kafka: KafkaPublisher) -> None:
        self._settings = settings
        self._kafka = kafka
        self._stop = asyncio.Event()
        self._calc = FlowCalculator(liquidity_pct=settings.binance_flow_liquidity_pct)
        self._status: dict[str, Any] = {
            "name": self.name,
            "running": False,
            "last_error": None,
            "trades_published": 0,
            "flow_published": 0,
        }

    @property
    def status(self) -> dict[str, Any]:
        return dict(self._status)

    def request_stop(self) -> None:
        self._stop.set()

    async def run(self) -> None:
        symbol = self._settings.binance_symbol.lower()
        stream = f"{symbol}@aggTrade/{symbol}@depth20@100ms"
        url = f"{self._settings.binance_combined_ws_url}?streams={stream}"
        self._status["running"] = True
        self._status["last_error"] = None
        logger.info("binance flow worker start symbol=%s", self._settings.binance_symbol)
        try:
            while not self._stop.is_set():
                try:
                    async with websockets.connect(url, ping_interval=20) as ws:
                        logger.info("binance flow ws connected %s", url)
                        while not self._stop.is_set():
                            raw = await asyncio.wait_for(ws.recv(), timeout=60)
                            msg = json.loads(raw)
                            await self._handle_stream(msg)
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self._status["last_error"] = str(exc)
                    logger.warning("binance flow ws error: %s; reconnect in 3s", exc)
                    await asyncio.sleep(3)
        finally:
            self._status["running"] = False

    async def _handle_stream(self, msg: dict[str, Any]) -> None:
        stream = msg.get("stream") or ""
        data = msg.get("data") or msg
        if "aggTrade" in stream or data.get("e") == "aggTrade":
            await self._on_trade(data)
        elif "depth" in stream or "bids" in data:
            await self._on_depth(data)

    async def _on_trade(self, data: dict[str, Any]) -> None:
        price = float(data["p"])
        qty = float(data["q"])
        side = _trade_side(bool(data.get("m")))
        event_time_ms = int(data.get("T") or data.get("E") or 0)
        symbol = self._settings.binance_symbol.upper()

        trade = {
            "symbol": symbol,
            "price": price,
            "quantity": qty,
            "side": side,
            "timestamp": event_time_ms,
        }
        await self._kafka.publish_json(
            self._settings.kafka_topic_market_trades,
            symbol,
            trade,
            wait=False,
        )
        self._status["trades_published"] += 1

        closed = self._calc.on_trade(price=price, qty=qty, side=side, event_time_ms=event_time_ms)
        if closed is not None:
            await self._publish_closed_second(closed, symbol)

    async def _on_depth(self, data: dict[str, Any]) -> None:
        bids = [(float(p), float(q)) for p, q in (data.get("bids") or [])]
        asks = [(float(p), float(q)) for p, q in (data.get("asks") or [])]
        self._calc.on_book(bids, asks)

    async def _publish_closed_second(self, closed: Any, symbol: str) -> None:
        snap = self._calc.snapshot(closed)
        snap["symbol"] = symbol
        snap["entity"] = "btc"
        snap["source"] = "binance"

        bid_liq, ask_liq = self._calc.liquidity_near_price(closed.last_price)
        book = {
            "symbol": symbol,
            "bucket_epoch": closed.epoch,
            "price": closed.last_price,
            "bid_liquidity": round(bid_liq, 8),
            "ask_liquidity": round(ask_liq, 8),
            "liquidity_pct": self._settings.binance_flow_liquidity_pct,
            "bids_top": [[p, q] for p, q in self._calc.bids[:10]],
            "asks_top": [[p, q] for p, q in self._calc.asks[:10]],
        }
        await self._kafka.publish_json(self._settings.kafka_topic_market_orderbook, symbol, book)
        await self._kafka.publish_json(self._settings.kafka_topic_market_flow, symbol, snap)
        self._status["flow_published"] += 1
        logger.debug(
            "flow %s delta=%s agr=%s reaction=%s",
            symbol,
            snap.get("delta"),
            snap.get("buy_aggression"),
            snap.get("reaction"),
        )
