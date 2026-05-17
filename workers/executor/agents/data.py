import logging

from shared.deriv_client import fetch_ticks_history
from shared.events import WorkflowSnapshot

logger = logging.getLogger(__name__)


async def fetch_market_data(snapshot: WorkflowSnapshot) -> dict:
    """Fetch Deriv ticks via credentials on the workflow snapshot."""
    token = (snapshot.deriv_api_token or "").strip()
    if not token:
        logger.warning("no deriv_api_token on snapshot; using stub market data")
        ticks = [100.0 + i * 0.15 for i in range(10)]
        return {
            "symbol": snapshot.trading_pair,
            "trading_type": snapshot.trading_type,
            "ticks": ticks,
            "last": ticks[-1],
            "source": "stub",
        }

    try:
        packet = await fetch_ticks_history(
            app_id=snapshot.deriv_app_id,
            token=token,
            symbol=snapshot.trading_pair,
            count=100,
        )
        packet["trading_type"] = snapshot.trading_type
        packet["source"] = "deriv"
        return packet
    except Exception as exc:
        logger.exception("Deriv market data failed: %s", exc)
        return {
            "symbol": snapshot.trading_pair,
            "trading_type": snapshot.trading_type,
            "ticks": [],
            "last": None,
            "source": "deriv_error",
            "error": str(exc),
        }
