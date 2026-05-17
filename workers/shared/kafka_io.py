import json
import logging
from collections.abc import AsyncIterator

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pydantic import BaseModel

from shared.settings import settings

logger = logging.getLogger(__name__)


def serialize_event(event: BaseModel) -> bytes:
    return event.model_dump_json().encode("utf-8")


async def create_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap)
    try:
        await producer.start()
    except Exception:
        logger.exception(
            "failed to connect Kafka producer bootstrap=%s",
            settings.kafka_bootstrap,
        )
        raise
    return producer


async def publish_event(
    producer: AIOKafkaProducer,
    topic: str,
    event: BaseModel,
    *,
    key: str,
) -> None:
    try:
        await producer.send_and_wait(
            topic,
            serialize_event(event),
            key=key.encode("utf-8"),
        )
    except Exception:
        logger.exception("failed to publish topic=%s key=%s", topic, key)
        raise


async def consume_json(topic: str, group_id: str) -> AsyncIterator[tuple[str, dict]]:
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.kafka_bootstrap,
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    try:
        await consumer.start()
    except Exception:
        logger.exception(
            "failed to connect Kafka consumer topic=%s group=%s bootstrap=%s",
            topic,
            group_id,
            settings.kafka_bootstrap,
        )
        raise

    try:
        async for message in consumer:
            try:
                key = message.key.decode("utf-8") if message.key else ""
                payload = json.loads(message.value.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                logger.exception("invalid message on topic=%s", topic)
                continue
            yield key, payload
    finally:
        await consumer.stop()