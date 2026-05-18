import logging
from uuid import uuid4

from app.core import config
from app.messaging.workflow_events import WorkflowScheduledEvent, WorkflowSnapshot
from app.models.workflow_model import Workflow

logger = logging.getLogger(__name__)


async def publish_workflow_scheduled(workflow: Workflow, user_id: str) -> str | None:
    if not config.KAFKA_ENABLED:
        logger.debug("Kafka disabled; skip workflow.scheduled publish")
        return None

    try:
        from aiokafka import AIOKafkaProducer
    except ImportError as exc:
        logger.error("aiokafka not installed: %s", exc)
        raise

    schedule_id = str(uuid4())
    snapshot = WorkflowSnapshot(
        workflow_id=workflow.id,
        user_id=user_id,
        name=workflow.name,
        trading_pair=workflow.trading_pair,
        trading_type=workflow.trading_type,
        starting_time=workflow.starting_time,
        one_day_minimum_trade=int(workflow.one_day_minimum_trade),
        graph_definition=workflow.graph_definition,
        deriv_app_id=workflow.deriv_app_id,
        deriv_api_token=workflow.deriv_api_token,
        risk_capital=float(workflow.risk_capital or 5.0),
        mm_cycle_trades=int(workflow.mm_cycle_trades or 10),
        mm_target_wins=int(workflow.mm_target_wins or 6),
        mm_payout=float(workflow.mm_payout or 1.95),
        account_currency=workflow.account_currency or "USD",
        contract_strategy=workflow.contract_strategy or "rise_fall",
        duration_ticks=int(workflow.duration_ticks or 2),
    )
    event = WorkflowScheduledEvent(schedule_id=schedule_id, snapshot=snapshot)

    producer = AIOKafkaProducer(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
    try:
        await producer.start()
        payload = event.model_dump_json().encode("utf-8")
        await producer.send_and_wait(
            config.KAFKA_TOPIC_SCHEDULED,
            payload,
            key=user_id.encode("utf-8"),
        )
    except Exception:
        logger.exception(
            "failed to publish workflow.scheduled schedule_id=%s workflow_id=%s",
            schedule_id,
            workflow.id,
        )
        raise
    finally:
        await producer.stop()

    logger.info(
        "published workflow.scheduled schedule_id=%s workflow_id=%s",
        schedule_id,
        workflow.id,
    )
    return schedule_id