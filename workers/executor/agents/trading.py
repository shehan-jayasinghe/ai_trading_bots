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
        stub_id = str(uuid4())
        outcome = "win" if int(stub_id.replace("-", "")[:8], 16) % 2 == 0 else "loss"
        return {
            "trade_id": stub_id,
            "status": "filled",
            "direction": action,
            "stake": stake,
            "symbol": snapshot.trading_pair,
            "source": "stub",
            "outcome": outcome,
        }

    try:
        placed = await place_rise_fall_trade(
            app_id=snapshot.deriv_app_id,
            token=token,
            symbol=snapshot.trading_pair,
            direction=action,
            stake=float(stake),
            duration=int(snapshot.duration_ticks or 2),
            currency=(snapshot.account_currency or "USD").upper(),
            contract_strategy=snapshot.contract_strategy or "rise_fall",
        )
        return {
            "trade_id": placed.get("contract_id") or str(uuid4()),
            "status": "filled",
            "direction": action,
            "stake": stake,
            "symbol": snapshot.trading_pair,
            "source": "deriv",
            "outcome": "pending",
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
