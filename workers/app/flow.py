from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class SecondBucket:
    epoch: int
    buy_volume: float = 0.0
    sell_volume: float = 0.0
    last_price: float = 0.0
    high: float = 0.0
    low: float = 0.0
    trade_count: int = 0

    def add_trade(self, price: float, qty: float, side: str) -> None:
        if side == "BUY":
            self.buy_volume += qty
        else:
            self.sell_volume += qty
        self.trade_count += 1
        self.last_price = price
        if self.high == 0.0:
            self.high = price
            self.low = price
        else:
            self.high = max(self.high, price)
            self.low = min(self.low, price)


def _aggression(buy: float, sell: float) -> float | None:
    total = buy + sell
    if total <= 0:
        return None
    return buy / total


def _imbalance(bid_liq: float, ask_liq: float) -> float | None:
    total = bid_liq + ask_liq
    if total <= 0:
        return None
    return (bid_liq - ask_liq) / total


def _pressure(aggression: float | None) -> str:
    if aggression is None:
        return "unknown"
    if aggression > 0.60:
        return "buying"
    if aggression < 0.40:
        return "selling"
    return "balanced"


@dataclass
class FlowCalculator:
    """Aggressive volume from trades; liquidity from order book. Never mix the two."""

    liquidity_pct: float = 0.005
    history: deque[SecondBucket] = field(default_factory=lambda: deque(maxlen=120))
    current: SecondBucket | None = None
    last_price: float = 0.0
    bids: list[tuple[float, float]] = field(default_factory=list)
    asks: list[tuple[float, float]] = field(default_factory=list)

    def on_book(self, bids: list[tuple[float, float]], asks: list[tuple[float, float]]) -> None:
        self.bids = bids
        self.asks = asks
        if bids:
            self.last_price = self.last_price or bids[0][0]
        if asks and not self.last_price:
            self.last_price = asks[0][0]

    def on_trade(self, *, price: float, qty: float, side: str, event_time_ms: int) -> SecondBucket | None:
        epoch = event_time_ms // 1000
        self.last_price = price
        closed: SecondBucket | None = None
        if self.current is None:
            self.current = SecondBucket(epoch=epoch, last_price=price, high=price, low=price)
        elif epoch > self.current.epoch:
            closed = self.current
            self.history.append(closed)
            self.current = SecondBucket(epoch=epoch, last_price=price, high=price, low=price)
        self.current.add_trade(price, qty, side)
        return closed

    def liquidity_near_price(self, price: float | None = None) -> tuple[float, float]:
        px = price or self.last_price
        if px <= 0:
            return 0.0, 0.0
        low = px * (1.0 - self.liquidity_pct)
        high = px * (1.0 + self.liquidity_pct)
        bid_liq = sum(qty for p, qty in self.bids if p >= low)
        ask_liq = sum(qty for p, qty in self.asks if p <= high)
        return bid_liq, ask_liq

    def _sum_windows(self, seconds: int) -> tuple[float, float, float, float]:
        if not self.history:
            return 0.0, 0.0, 0.0, 0.0
        latest = self.history[-1].epoch
        buy = sell = 0.0
        high = 0.0
        low = 0.0
        for bucket in self.history:
            if latest - bucket.epoch >= seconds:
                continue
            buy += bucket.buy_volume
            sell += bucket.sell_volume
            if high == 0.0:
                high = bucket.high
                low = bucket.low
            else:
                high = max(high, bucket.high)
                low = min(low, bucket.low)
        return buy, sell, high, low

    def reaction(self, closed: SecondBucket, bid_liq: float, ask_liq: float) -> str:
        buy5, sell5, high5, low5 = self._sum_windows(5)
        px = closed.last_price
        if px <= 0:
            return "none"
        bid_zone = px * (1.0 - self.liquidity_pct)
        ask_zone = px * (1.0 + self.liquidity_pct)
        sold_hard = sell5 > buy5 and sell5 > 0
        bought_hard = buy5 > sell5 and buy5 > 0
        swept_bids = low5 > 0 and low5 <= bid_zone and px > bid_zone and sold_hard and bid_liq > ask_liq
        swept_asks = high5 >= ask_zone and px < ask_zone and bought_hard and ask_liq > bid_liq
        if swept_bids:
            return "sell_absorbed_reclaim"
        if swept_asks:
            return "buy_absorbed_reject"
        return "none"

    def snapshot(self, closed: SecondBucket) -> dict:
        bid_liq, ask_liq = self.liquidity_near_price(closed.last_price)
        buy, sell = closed.buy_volume, closed.sell_volume
        delta = buy - sell
        agr = _aggression(buy, sell)
        imb = _imbalance(bid_liq, ask_liq)
        buy5, sell5, _, _ = self._sum_windows(5)
        buy15, sell15, _, _ = self._sum_windows(15)
        buy60, sell60, _, _ = self._sum_windows(60)
        reaction = self.reaction(closed, bid_liq, ask_liq)
        return {
            "symbol": None,  # filled by worker
            "window_sec": 1,
            "bucket_epoch": closed.epoch,
            "price": closed.last_price,
            "buy_volume": round(buy, 8),
            "sell_volume": round(sell, 8),
            "delta": round(delta, 8),
            "buy_aggression": None if agr is None else round(agr, 4),
            "pressure": _pressure(agr),
            "bid_liquidity": round(bid_liq, 8),
            "ask_liquidity": round(ask_liq, 8),
            "liquidity_imbalance": None if imb is None else round(imb, 4),
            "reaction": reaction,
            "windows": {
                "5s": {
                    "buy_volume": round(buy5, 8),
                    "sell_volume": round(sell5, 8),
                    "delta": round(buy5 - sell5, 8),
                    "buy_aggression": None if _aggression(buy5, sell5) is None else round(_aggression(buy5, sell5), 4),
                },
                "15s": {
                    "buy_volume": round(buy15, 8),
                    "sell_volume": round(sell15, 8),
                    "delta": round(buy15 - sell15, 8),
                    "buy_aggression": None if _aggression(buy15, sell15) is None else round(_aggression(buy15, sell15), 4),
                },
                "1m": {
                    "buy_volume": round(buy60, 8),
                    "sell_volume": round(sell60, 8),
                    "delta": round(buy60 - sell60, 8),
                    "buy_aggression": None if _aggression(buy60, sell60) is None else round(_aggression(buy60, sell60), 4),
                },
            },
        }
