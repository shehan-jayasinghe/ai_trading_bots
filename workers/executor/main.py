import asyncio
import logging

from executor.graph import run_one_attempt
from shared.events import WorkflowExecuteEvent
from shared.kafka_io import consume_json
from shared.settings import settings
from shared.workflow_store import save_last_trade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("executor")


async def handle_execute(data: dict) -> None:
    event = WorkflowExecuteEvent.model_validate(data)
    one_day_minimum_trade = event.snapshot.one_day_minimum_trade
    trades_done = 0
    logger.info(
        "run started run_id=%s workflow=%s one_day_minimum_trade=%s",
        event.run_id,
        event.snapshot.workflow_id,
        one_day_minimum_trade,
    )

    while trades_done < one_day_minimum_trade:
        result = await run_one_attempt(event.snapshot, event.run_id)
        trade_result = result.trade_result or {}
        if trade_result and trade_result.get("status") in ("filled", "error"):
            await save_last_trade(
                event.snapshot.workflow_id,
                run_id=event.run_id,
                trade_result=trade_result,
            )
        if trade_result.get("status") == "filled":
            trades_done += 1
        logger.info(
            "attempt=%s action=%s trades_done=%s/%s",
            result.attempt_id,
            (result.decision or {}).get("action"),
            trades_done,
            one_day_minimum_trade,
        )
        if result.error:
            logger.error("attempt error: %s", result.error)
            break

    logger.info("run finished run_id=%s trades_done=%s", event.run_id, trades_done)


async def main() -> None:
    logger.info("executor listening on %s", settings.topic_execute)
    async for _key, data in consume_json(settings.topic_execute, "executor-agent"):
        try:
            await handle_execute(data)
        except Exception:
            logger.exception("execute handler failed")


if __name__ == "__main__":
    asyncio.run(main())
