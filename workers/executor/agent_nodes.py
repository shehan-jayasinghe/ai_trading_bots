"""LangGraph node handlers (one function per agent kind)."""
from typing import Any, Awaitable, Callable

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
    state.market_packet = await fetch_market_data(state.snapshot)
    return state


async def node_indicator(state: TradeState) -> TradeState:
    state.indicator_signal = compute_indicator(state.market_packet)
    return state


async def node_rag(state: TradeState) -> TradeState:
    state.rag_context = await load_rag(state.snapshot)
    return state


async def node_decision(state: TradeState) -> TradeState:
    state.decision = await run_decision(
        state.snapshot,
        state.market_packet,
        state.indicator_signal,
        state.rag_context,
    )
    return state


async def node_mm(state: TradeState) -> TradeState:
    stake, session, meta = await compute_stake(
        state.snapshot, state.decision, state.mm_session
    )
    state.stake = stake
    state.mm_session = session
    state.mm_meta = meta
    return state


async def node_trade(state: TradeState) -> TradeState:
    state.trade_result = await execute_trade(
        state.snapshot,
        state.decision,
        state.stake,
    )
    return state


async def node_rag_write(state: TradeState) -> TradeState:
    await save_rag(state.snapshot, state.trade_result)
    return state


AGENT_HANDLERS: dict[str, Callable[[TradeState], Awaitable[TradeState]]] = {
    "data": node_data,
    "indicator": node_indicator,
    "rag": node_rag,
    "decision": node_decision,
    "mm": node_mm,
    "trading": node_trade,
    "rag_write": node_rag_write,
}
