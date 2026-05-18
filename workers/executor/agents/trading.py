import logging
from uuid import uuid4

from shared.deriv_client import place_rise_fall_trade, wait_for_settlement
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
            "profit": stake * 0.95 if outcome == "win" else -stake,
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
        contract_id = placed.get("contract_id")
        trade_result = {
            "trade_id": contract_id or str(uuid4()),
            "status": "filled",
            "direction": action,
            "stake": stake,
            "symbol": snapshot.trading_pair,
            "source": "deriv",
            "outcome": "pending",
            **placed,
        }

        if contract_id:
            logger.info("waiting for contract settlement contract_id=%s", contract_id)
            settlement = await wait_for_settlement(
                app_id=snapshot.deriv_app_id,
                token=token,
                contract_id=str(contract_id),
                poll_interval=1.0,
                timeout_sec=120.0,
            )
            trade_result.update(settlement)
            if settlement.get("outcome") in ("win", "loss"):
                trade_result["status"] = "settled"

        return trade_result
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
