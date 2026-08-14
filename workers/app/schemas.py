from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field


class MarketEnvelope(BaseModel):
    entity: str
    source: str
    symbol: str
    timeframe: str
    bucket_epoch: int
    event_time_ms: int
    payload: dict[str, Any] = Field(default_factory=dict)

    def partition_key(self) -> str:
        return f"{self.entity}|{self.timeframe}|{self.bucket_epoch}"

    def to_kafka_value(self) -> bytes:
        return json.dumps(self.model_dump(), separators=(",", ":")).encode("utf-8")


def timeframe_seconds(tf: str) -> int:
    unit = tf[-1]
    amount = int(tf[:-1])
    if unit == "s":
        return amount
    if unit == "m":
        return amount * 60
    if unit == "h":
        return amount * 3600
    raise ValueError(f"unsupported timeframe: {tf}")


def floor_epoch(epoch_sec: int, tf: str) -> int:
    step = timeframe_seconds(tf)
    return epoch_sec - (epoch_sec % step)
