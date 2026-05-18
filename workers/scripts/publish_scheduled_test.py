"""Publish a test workflow.scheduled event."""
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from shared.events import WorkflowScheduledEvent, WorkflowSnapshot
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
        one_day_minimum_trade=2,
        risk_capital=5.0,
        mm_cycle_trades=10,
        mm_target_wins=6,
        mm_payout=1.95,
        account_currency="USD",
        contract_strategy="rise_fall",
        duration_ticks=2,
    )
    event = WorkflowScheduledEvent(schedule_id=str(uuid4()), snapshot=snapshot)
    producer = await create_producer()
    try:
        await publish_event(
            producer, settings.topic_scheduled, event, key=snapshot.user_id
        )
    finally:
        await producer.stop()
    print(f"published {settings.topic_scheduled} schedule_id={event.schedule_id}")


if __name__ == "__main__":
    asyncio.run(main())
