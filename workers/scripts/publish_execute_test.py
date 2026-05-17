"""Publish a test workflow.execute event (bypass planner clock)."""
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from shared.events import WorkflowExecuteEvent, WorkflowSnapshot
from shared.kafka_io import create_producer, publish_event
from shared.settings import settings


async def main() -> None:
    snapshot = WorkflowSnapshot(
        workflow_id="test-workflow",
        user_id="test-user",
        name="Test Bot",
        trading_pair="R_100",
        trading_type="binary",
        starting_time=datetime.now(timezone.utc),
        one_day_minimum_trade=1,
    )
    event = WorkflowExecuteEvent(
        schedule_id="test-schedule",
        run_id=str(uuid4()),
        run_date=datetime.now(timezone.utc).date().isoformat(),
        snapshot=snapshot,
    )
    producer = await create_producer()
    try:
        await publish_event(producer, settings.topic_execute, event, key=snapshot.user_id)
    finally:
        await producer.stop()
    print(f"published {settings.topic_execute} run_id={event.run_id}")


if __name__ == "__main__":
    asyncio.run(main())
