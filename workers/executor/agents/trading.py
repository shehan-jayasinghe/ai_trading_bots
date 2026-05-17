import logging
from uuid import uuid4

from shared.deriv_client import place_rise_fall_trade
from shared.events import WorkflowSnapshot

logger = logging.getLogger(__name__)


async def execute_trade(
    snapshot: WorkflowSnapshot,
    decision: dict,
    stake: float,
) -> dict:
    action = decision.get("action", "skip")
    if action == "skip" or stake <= 0:
        return {"trade_id": None, "status": "skipped", "direction": None}

    token = (snapshot.deriv_api_token or "").strip()
    if not token:
        return {
            "trade_id": str(uuid4()),
            "status": "filled",
            "direction": action,
            "stake": stake,
            "symbol": snapshot.trading_pair,
            "source": "stub",
        }

    try:
        placed = await place_rise_fall_trade(
            app_id=snapshot.deriv_app_id,
            token=token,
            symbol=snapshot.trading_pair,
            direction=action,
            stake=float(stake),
        )
        return {
            "trade_id": placed.get("contract_id") or str(uuid4()),
            "status": "filled",
            "direction": action,
            "stake": stake,
            "symbol": snapshot.trading_pair,
            "source": "deriv",
            **placed,
        }
    except Exception as exc:
        logger.exception("Deriv trade failed: %s", exc)
        return {
            "trade_id": None,
            "status": "error",
            "direction": action,
            "stake": stake,
            "symbol": snapshot.trading_pair,
            "source": "deriv_error",
            "error": str(exc),
        }
