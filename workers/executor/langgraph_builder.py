"""Validate editor JSON and compile a LangGraph StateGraph (node id = LangGraph name)."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Awaitable

from langgraph.graph import END, StateGraph

from executor.agent_nodes import AGENT_HANDLERS, ALLOWED_AGENT_KINDS
from shared.trade_state import TradeState

logger = logging.getLogger(__name__)

REQUIRED_AGENT_KINDS = frozenset({"data", "decision", "trading"})


def _agent_kind(node: dict[str, Any]) -> str | None:
    if node.get("type") != "agent":
        return None
    return (node.get("data") or {}).get("agentKind")


def _top_level(defn: dict[str, Any]) -> list[dict[str, Any]]:
    return [n for n in (defn.get("nodes") or []) if not n.get("parentId")]


def _parallel_children(defn: dict[str, Any], parallel_id: str) -> list[dict[str, Any]]:
    return [
        n
        for n in (defn.get("nodes") or [])
        if n.get("parentId") == parallel_id and n.get("type") == "agent"
    ]


def _all_agent_kinds(defn: dict[str, Any]) -> set[str]:
    kinds: set[str] = set()
    for node in defn.get("nodes") or []:
        kind = _agent_kind(node)
        if kind:
            kinds.add(kind)
    return kinds


def validate_editor_graph(defn: dict[str, Any]) -> list[str]:
    """Minimal checks: structure + known agents + required data/decision/trading."""
    if not defn:
        return ["Graph definition is missing"]

    nodes = defn.get("nodes") or []
    if not nodes:
        return ["Graph must contain at least one node"]

    errors: list[str] = []
    node_ids = [n["id"] for n in nodes]
    if len(node_ids) != len(set(node_ids)):
        errors.append("Duplicate node ids in graph")

    id_set = set(node_ids)
    for edge in defn.get("edges") or []:
        if edge.get("source") not in id_set or edge.get("target") not in id_set:
            errors.append(f"Edge {edge.get('id', '?')} references unknown node")
        if edge.get("source") == edge.get("target"):
            errors.append(f"Edge {edge.get('id', '?')} cannot connect a node to itself")

    for node in nodes:
        if node.get("type") == "agent":
            kind = _agent_kind(node)
            if not kind or kind not in ALLOWED_AGENT_KINDS:
                errors.append(f"Node {node['id']} has unknown agentKind")
            elif kind not in AGENT_HANDLERS:
                errors.append(f"No handler for agentKind {kind!r}")
        elif node.get("type") == "parallel":
            if not _parallel_children(defn, node["id"]):
                errors.append(f"Parallel group {node['id']} has no agents inside")

    kinds = _all_agent_kinds(defn)
    for required in REQUIRED_AGENT_KINDS:
        if required not in kinds:
            errors.append(f"Graph must include at least one {required!r} agent")

    if not _top_level(defn):
        errors.append("Graph must have at least one top-level node")

    return errors


def _parallel_runner(defn: dict[str, Any], parallel_id: str) -> Callable[[TradeState], Awaitable[TradeState]]:
    async def run_parallel(state: TradeState) -> TradeState:
        children = _parallel_children(defn, parallel_id)
        if not children:
            return state

        async def run_child(child: dict[str, Any]) -> TradeState:
            kind = _agent_kind(child)
            handler = AGENT_HANDLERS.get(kind or "")
            if not handler:
                raise ValueError(f"Unknown agent kind: {kind}")
            return await handler(state.model_copy(deep=True))

        merged = state.model_copy(deep=True)
        for partial in await asyncio.gather(*[run_child(c) for c in children]):
            for key in (
                "market_packet",
                "indicator_signal",
                "rag_context",
                "decision",
                "stake",
                "trade_result",
            ):
                value = getattr(partial, key)
                if value:
                    setattr(merged, key, value)
        return merged

    return run_parallel


def _decision_router(next_node_id: str) -> Callable[[TradeState], str]:
    def route(state: TradeState) -> str:
        if (state.decision or {}).get("action", "skip") == "skip":
            return "__end__"
        return next_node_id

    return route


def build_langgraph(defn: dict[str, Any]):
    errors = validate_editor_graph(defn)
    if errors:
        raise ValueError("; ".join(errors))

    top = _top_level(defn)
    top_by_id = {u["id"]: u for u in top}
    top_ids = set(top_by_id.keys())
    edges = [e for e in (defn.get("edges") or []) if e.get("source") in top_ids and e.get("target") in top_ids]

    outgoing: dict[str, list[str]] = {uid: [] for uid in top_ids}
    incoming: dict[str, list[str]] = {uid: [] for uid in top_ids}
    for edge in edges:
        outgoing[edge["source"]].append(edge["target"])
        incoming[edge["target"]].append(edge["source"])

    graph = StateGraph(TradeState)

    for unit in top:
        nid = unit["id"]
        if unit.get("type") == "parallel":
            graph.add_node(nid, _parallel_runner(defn, nid))
            continue
        kind = _agent_kind(unit)
        if not kind:
            raise ValueError(f"Top-level agent {nid} missing agentKind")
        graph.add_node(nid, AGENT_HANDLERS[kind])

    decision_ids = {u["id"] for u in top if _agent_kind(u) == "decision"}

    for edge in edges:
        src, tgt = edge["source"], edge["target"]
        if _agent_kind(top_by_id[src]) == "decision":
            continue
        graph.add_edge(src, tgt)

    for did in decision_ids:
        targets = outgoing.get(did) or []
        if not targets:
            graph.add_conditional_edges(did, _decision_router("__end__"), {"__end__": END})
            continue
        next_id = targets[0]
        graph.add_conditional_edges(
            did,
            _decision_router(next_id),
            {next_id: next_id, "__end__": END},
        )

    for uid in top_ids:
        if not outgoing[uid] and uid not in decision_ids:
            graph.add_edge(uid, END)

    entries = [uid for uid in top_ids if not incoming[uid]]
    if not entries:
        raise ValueError("Graph has no entry node (every node has an incoming edge)")
    graph.set_entry_point(entries[0])

    logger.info("compiled LangGraph nodes=%s entry=%s", list(top_ids), entries[0])
    return graph.compile()
