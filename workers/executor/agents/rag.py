import logging

from shared.events import WorkflowSnapshot

logger = logging.getLogger(__name__)


async def load_rag(snapshot: WorkflowSnapshot) -> dict:
    """TODO: load last N trades from Postgres/pgvector for workflow_id."""
    _ = snapshot
    trades: list[dict] = []
    if not trades:
        return {"trading_id": None, "snippets": []}
    return {"trading_id": trades[-1].get("id"), "snippets": trades}


async def save_rag(snapshot: WorkflowSnapshot, trade_result: dict) -> None:
    """Persist closed trade context for RAG (embed + upsert when store exists)."""
    if not trade_result.get("trade_id"):
        return
    if trade_result.get("outcome") not in ("win", "loss"):
        logger.debug("skip RAG write until trade settled outcome=%s", trade_result.get("outcome"))
        return
    logger.info(
        "RAG write workflow=%s trade_id=%s outcome=%s profit=%s",
        snapshot.workflow_id,
        trade_result.get("trade_id"),
        trade_result.get("outcome"),
        trade_result.get("profit"),
    )
    # TODO: embed + upsert to pgvector
