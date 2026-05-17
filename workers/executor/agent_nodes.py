"""LangGraph node handlers (one function per agent kind)."""
from typing import Any

from executor.agents.data import fetch_market_data
from executor.agents.decision_crew import run_decision
from executor.agents.indicator import compute_indicator
from executor.agents.mm import compute_stake
from executor.agents.rag import load_rag, save_rag
from executor.agents.trading import execute_trade
from shared.trade_state import TradeState

ALLOWED_AGENT_KINDS = frozenset(
    {"data", "indicator", "rag", "decision", "mm", "trading", "rag_write"}
)


async def node_data(state: TradeState) -> TradeState:
    state["market_packet"] = await fetch_market_data(state["snapshot"])
    return state


async def node_indicator(state: TradeState) -> TradeState:
    state["indicator_signal"] = compute_indicator(state.get("market_packet", {}))
    return state


async def node_rag(state: TradeState) -> TradeState:
    state["rag_context"] = await load_rag(state["snapshot"])
    return state


async def node_decision(state: TradeState) -> TradeState:
    state["decision"] = await run_decision(
        state["snapshot"],
        state.get("market_packet", {}),
        state.get("indicator_signal", {}),
        state.get("rag_context", {}),
    )
    return state


async def node_mm(state: TradeState) -> TradeState:
    state["stake"] = await compute_stake(state["snapshot"], state.get("decision", {}))
    return state


async def node_trade(state: TradeState) -> TradeState:
    state["trade_result"] = await execute_trade(
        state["snapshot"],
        state.get("decision", {}),
        state.get("stake", 0.0),
    )
    return state


async def node_rag_write(state: TradeState) -> TradeState:
    await save_rag(state["snapshot"], state.get("trade_result", {}))
    return state


AGENT_HANDLERS: dict[str, Any] = {
    "data": node_data,
    "indicator": node_indicator,
    "rag": node_rag,
    "decision": node_decision,
    "mm": node_mm,
    "trading": node_trade,
    "rag_write": node_rag_write,
}
