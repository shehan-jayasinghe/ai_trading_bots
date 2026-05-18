import asyncio
import logging

from executor.graph import run_one_attempt
from shared.events import WorkflowExecuteEvent
from shared.kafka_io import consume_json
from shared.masaniello import apply_trade_outcome, session_from_snapshot
from shared.settings import settings
from shared.workflow_store import save_last_trade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("executor")


def _infer_outcome(trade_result: dict) -> str:
    explicit = trade_result.get("outcome")
    if explicit in ("win", "loss", "pending"):
        return explicit
    profit = trade_result.get("profit")
    if profit is not None:
        return "win" if float(profit) > 0 else "loss"
    return "pending"


async def handle_execute(data: dict) -> None:
    event = WorkflowExecuteEvent.model_validate(data)
    one_day_minimum_trade = event.snapshot.one_day_minimum_trade
    trades_done = 0
    mm_session = session_from_snapshot(event.snapshot)

    logger.info(
        "run started run_id=%s workflow=%s one_day_minimum_trade=%s mm_capital=%s",
        event.run_id,
        event.snapshot.workflow_id,
        one_day_minimum_trade,
        mm_session.capital,
    )

    while trades_done < one_day_minimum_trade:
        result = await run_one_attempt(event.snapshot, event.run_id, mm_session)
        if result.mm_session is not None:
            mm_session = result.mm_session

        trade_result = result.trade_result or {}
        if trade_result and trade_result.get("status") in ("filled", "error"):
            await save_last_trade(
                event.snapshot.workflow_id,
                run_id=event.run_id,
                trade_result=trade_result,
            )

        status = trade_result.get("status")
        if status == "filled":
            trades_done += 1
            outcome = _infer_outcome(trade_result)
            stake = float(trade_result.get("stake") or result.stake or 0)
            if outcome in ("win", "loss") and stake > 0:
                mm_session = apply_trade_outcome(
                    mm_session, stake=stake, outcome=outcome
                )
                logger.info(
                    "mm updated outcome=%s capital=%.2f wins=%s losses=%s",
                    outcome,
                    mm_session.capital,
                    mm_session.wins,
                    mm_session.losses,
                )
            elif outcome == "pending":
                logger.info(
                    "contract filled; outcome pending (mm capital unchanged until settlement)"
                )

        logger.info(
            "attempt=%s action=%s stake=%s trades_done=%s/%s mm_capital=%.2f",
            result.attempt_id,
            (result.decision or {}).get("action"),
            result.stake,
            trades_done,
            one_day_minimum_trade,
            mm_session.capital,
        )

        if mm_session.trades_played >= mm_session.cycle_trades:
            logger.info("mm cycle complete; resetting session capital")
            mm_session = session_from_snapshot(event.snapshot)

        if result.error:
            logger.error("attempt error: %s", result.error)
            break

        if status == "error":
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
