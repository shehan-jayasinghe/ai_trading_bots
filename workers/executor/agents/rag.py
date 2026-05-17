from shared.events import WorkflowSnapshot


async def load_rag(snapshot: WorkflowSnapshot) -> dict:
    """TODO: load last N trades from Postgres/pgvector for workflow_id."""
    _ = snapshot
    trades: list[dict] = []
    if not trades:
        return {"trading_id": None, "snippets": []}
    return {"trading_id": trades[-1].get("id"), "snippets": trades}


async def save_rag(snapshot: WorkflowSnapshot, trade_result: dict) -> None:
    """TODO: embed + upsert after closed trade."""
    if not trade_result.get("trade_id"):
        return
    _ = snapshot
