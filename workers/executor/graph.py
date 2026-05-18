from typing import Any, cast
from uuid import uuid4

from executor.langgraph_builder import build_langgraph
from shared.events import WorkflowSnapshot
from shared.masaniello import MmSession
from shared.trade_state import TradeState


async def run_one_attempt(
    snapshot: WorkflowSnapshot,
    run_id: str,
    mm_session: MmSession | None = None,
) -> TradeState:
    initial = TradeState(
        run_id=run_id,
        attempt_id=str(uuid4()),
        snapshot=snapshot,
        mm_session=mm_session,
    )

    defn: dict[str, Any] | None = snapshot.graph_definition
    if defn is None:
        raise ValueError("Workflow snapshot has no graph; save the graph in the editor first")

    compiled = build_langgraph(cast(dict[str, Any], defn))
    raw = await compiled.ainvoke(initial)
    if isinstance(raw, TradeState):
        return raw
    return TradeState.model_validate(raw)
