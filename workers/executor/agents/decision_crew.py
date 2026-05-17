import asyncio
import json
import os
from typing import Any

from shared.events import WorkflowSnapshot
from shared.settings import settings


def _angle_vote(market: dict) -> str:
    ticks = market.get("ticks") or []
    if len(ticks) < 3:
        return "skip"
    deltas = [ticks[i] - ticks[i - 1] for i in range(1, len(ticks))]
    last_two = deltas[-2:]
    if all(d > 10 for d in last_two):
        return "up"
    if all(d < -10 for d in last_two):
        return "down"
    return "neutral"


def _indicator_vote(indicator: dict) -> str:
    direction = indicator.get("direction", "neutral")
    if direction == "up":
        return "call"
    if direction == "down":
        return "put"
    return "skip"


def _rag_vote(rag: dict) -> str:
    if rag.get("trading_id") is None:
        return "skip"
    return "neutral"


def _merge_votes(votes: list[str]) -> dict[str, Any]:
    actionable = [v for v in votes if v in ("call", "put", "up", "down")]
    if not actionable:
        return {"action": "skip", "confidence": 0.0, "reason": "no consensus", "votes": votes}

    normalized = ["call" if v in ("up", "call") else "put" for v in actionable]
    call_count = normalized.count("call")
    put_count = normalized.count("put")
    if call_count == put_count:
        return {"action": "skip", "confidence": 0.3, "reason": "tie", "votes": votes}
    action = "call" if call_count > put_count else "put"
    total = call_count + put_count
    confidence = max(call_count, put_count) / total
    return {"action": action, "confidence": confidence, "reason": "rule majority", "votes": votes}


def run_rules_decision(
    snapshot: WorkflowSnapshot,
    market: dict,
    indicator: dict,
    rag: dict,
) -> dict[str, Any]:
    _ = snapshot
    votes = [
        _indicator_vote(indicator),
        _angle_vote(market),
        _rag_vote(rag),
    ]
    return _merge_votes(votes)


def _run_crewai_decision(
    snapshot: WorkflowSnapshot,
    market: dict,
    indicator: dict,
    rag: dict,
) -> dict[str, Any]:
    from crewai import Agent, Crew, Process, Task

    context = json.dumps(
        {"workflow": snapshot.name, "market": market, "indicator": indicator, "rag": rag}
    )
    indicator_agent = Agent(
        role="Indicator Analyst",
        goal="Vote call, put, or skip from indicator_signal",
        backstory="Use indicator only.",
        verbose=False,
    )
    decider = Agent(
        role="Decision Lead",
        goal='Output JSON only: {"action":"call|put|skip","confidence":0-1,"reason":"..."}',
        backstory="Merge analyst input.",
        verbose=False,
    )
    t1 = Task(
        description=f"Vote from indicator. Context: {context}",
        agent=indicator_agent,
        expected_output="call, put, or skip",
    )
    t2 = Task(
        description="Merge into JSON action.",
        agent=decider,
        expected_output="JSON",
        context=[t1],
    )
    crew = Crew(agents=[indicator_agent, decider], tasks=[t1, t2], process=Process.sequential)
    raw = str(crew.kickoff())
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return run_rules_decision(snapshot, market, indicator, rag)


def run_decision_sync(
    snapshot: WorkflowSnapshot,
    market: dict,
    indicator: dict,
    rag: dict,
) -> dict[str, Any]:
    api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return run_rules_decision(snapshot, market, indicator, rag)
    os.environ["OPENAI_API_KEY"] = api_key
    try:
        return _run_crewai_decision(snapshot, market, indicator, rag)
    except ImportError:
        return run_rules_decision(snapshot, market, indicator, rag)
    except Exception:
        return run_rules_decision(snapshot, market, indicator, rag)


async def run_decision(
    snapshot: WorkflowSnapshot,
    market: dict,
    indicator: dict,
    rag: dict,
) -> dict[str, Any]:
    return await asyncio.to_thread(run_decision_sync, snapshot, market, indicator, rag)
