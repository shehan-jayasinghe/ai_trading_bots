import asyncio
import logging
from datetime import date
from uuid import uuid4

from shared.events import WorkflowExecuteEvent, WorkflowScheduledEvent
from shared.kafka_io import consume_json, create_producer, publish_event
from shared.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("planner")

# Temporary bridge until AWS EventBridge replaces this worker.
EXECUTE_DELAY_SECONDS = 10


async def handle_scheduled(producer, data: dict) -> None:
    event = WorkflowScheduledEvent.model_validate(data)
    logger.info(
        "scheduled received schedule_id=%s workflow=%s",
        event.schedule_id,
        event.snapshot.workflow_id,
    )

    await asyncio.sleep(EXECUTE_DELAY_SECONDS)

    user_id = event.snapshot.user_id
    run_id = str(uuid4())
    execute = WorkflowExecuteEvent(
        schedule_id=event.schedule_id,
        run_id=run_id,
        run_date=date.today().isoformat(),
        snapshot=event.snapshot,
    )
    await publish_event(
        producer,
        settings.topic_execute,
        execute,
        key=user_id,
    )
    logger.info("published execute run_id=%s schedule_id=%s", run_id, event.schedule_id)


async def main() -> None:
    producer = await create_producer()
    logger.info("planner started delay=%ss", EXECUTE_DELAY_SECONDS)
    async for _key, data in consume_json(settings.topic_scheduled, "planner-agent"):
        try:
            await handle_scheduled(producer, data)
        except Exception:
            logger.exception("scheduled handler failed")


if __name__ == "__main__":
    asyncio.run(main())