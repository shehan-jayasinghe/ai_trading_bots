from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.schemas import MarketEnvelope, floor_epoch

logger = logging.getLogger(__name__)


@dataclass
class CandleState:
    timeframe: str
    bucket_epoch: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    trade_count: int = 0

    def update(self, price: float, qty: float = 0.0) -> None:
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price
        self.volume += qty
        self.trade_count += 1

    def to_payload(self) -> dict:
        return {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "trade_count": self.trade_count,
        }


@dataclass
class MultiTimeframeCandleBuilder:
    """Build OHLCV candles for many TFs from a live price stream."""

    timeframes: list[str]
    entity: str
    source: str
    symbol: str
    _candles: dict[str, CandleState] = field(default_factory=dict)

    def on_price(
        self,
        *,
        price: float,
        qty: float,
        event_time_ms: int,
    ) -> list[MarketEnvelope]:
        """Update open candles; return envelopes for any candles that just closed."""
        closed: list[MarketEnvelope] = []
        epoch_sec = event_time_ms // 1000

        for tf in self.timeframes:
            bucket = floor_epoch(epoch_sec, tf)
            current = self._candles.get(tf)
            if current is None:
                self._candles[tf] = CandleState(
                    timeframe=tf,
                    bucket_epoch=bucket,
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    volume=qty,
                    trade_count=1,
                )
                continue

            if bucket > current.bucket_epoch:
                closed.append(
                    MarketEnvelope(
                        entity=self.entity,
                        source=self.source,
                        symbol=self.symbol,
                        timeframe=tf,
                        bucket_epoch=current.bucket_epoch,
                        event_time_ms=event_time_ms,
                        payload=current.to_payload(),
                    )
                )
                self._candles[tf] = CandleState(
                    timeframe=tf,
                    bucket_epoch=bucket,
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    volume=qty,
                    trade_count=1,
                )
            else:
                current.update(price, qty)

        return closed

    def snapshot_open(self, event_time_ms: int) -> list[MarketEnvelope]:
        out: list[MarketEnvelope] = []
        for tf, c in self._candles.items():
            out.append(
                MarketEnvelope(
                    entity=self.entity,
                    source=self.source,
                    symbol=self.symbol,
                    timeframe=tf,
                    bucket_epoch=c.bucket_epoch,
                    event_time_ms=event_time_ms,
                    payload=c.to_payload(),
                )
            )
        return out
