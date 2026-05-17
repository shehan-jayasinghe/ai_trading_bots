from uuid import uuid4

from executor.langgraph_builder import build_langgraph
from shared.events import WorkflowSnapshot
from shared.trade_state import TradeState


async def run_one_attempt(snapshot: WorkflowSnapshot, run_id: str) -> TradeState:
    initial: TradeState = {
        "run_id": run_id,
        "attempt_id": str(uuid4()),
        "snapshot": snapshot,
        "market_packet": {},
        "indicator_signal": {},
        "rag_context": {},
        "decision": {},
        "stake": 0.0,
        "trade_result": {},
        "error": None,
    }

    if not snapshot.graph_definition:
        raise ValueError("Workflow snapshot has no graph; save the graph in the editor first")

    compiled = build_langgraph(snapshot.graph_definition)
    return await compiled.ainvoke(initial)
