from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from aiokafka import AIOKafkaProducer

from app.schemas import MarketEnvelope

if TYPE_CHECKING:
    from app.settings import Settings

logger = logging.getLogger(__name__)


class KafkaPublisher:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._settings.kafka_bootstrap_servers,
            acks="all",
            linger_ms=5,
        )
        await self._producer.start()
        logger.info(
            "kafka producer started bootstrap=%s",
            self._settings.kafka_bootstrap_servers,
        )

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
            logger.info("kafka producer stopped")

    async def publish(self, topic: str, envelope: MarketEnvelope) -> None:
        if self._producer is None:
            raise RuntimeError("KafkaPublisher not started")
        key = envelope.partition_key().encode("utf-8")
        await self._producer.send_and_wait(topic, value=envelope.to_kafka_value(), key=key)
        logger.debug(
            "published topic=%s key=%s entity=%s tf=%s",
            topic,
            envelope.partition_key(),
            envelope.entity,
            envelope.timeframe,
        )

    async def publish_json(self, topic: str, key: str, payload: dict[str, Any], *, wait: bool = True) -> None:
        if self._producer is None:
            raise RuntimeError("KafkaPublisher not started")
        value = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        key_bytes = key.encode("utf-8")
        if wait:
            await self._producer.send_and_wait(topic, value=value, key=key_bytes)
        else:
            await self._producer.send(topic, value=value, key=key_bytes)
