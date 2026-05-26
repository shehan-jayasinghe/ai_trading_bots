import asyncio
import logging
import os
from typing import Any

from crewai import LLM
from shared.events import WorkflowSnapshot
from shared.schemas.decision import (
    DecisionContext,
    TradeDecision,
    crew_decision_to_state_dict,
    rules_decision_to_state_dict,
)
from shared.settings import settings

logger = logging.getLogger(__name__)


def _tick_value(tick: Any) -> float:
    if isinstance(tick, dict):
        return float(tick.get("price") or 0)
    return float(tick)


def _angle_vote(market: dict[str, Any]) -> str:
    raw = market.get("prices") or market.get("ticks") or []
    ticks = (
        [float(p) for p in raw]
        if raw and isinstance(raw[0], (int, float))
        else [_tick_value(t) for t in raw]
    )
    if len(ticks) < 3:
        return "skip"
    deltas = [ticks[i] - ticks[i - 1] for i in range(1, len(ticks))]
    last_two = deltas[-2:]
    if all(d > 10 for d in last_two):
        return "up"
    if all(d < -10 for d in last_two):
        return "down"
    return "neutral"


def _indicator_vote(indicator: dict[str, Any]) -> str:
    direction = indicator.get("direction", "neutral")
    if direction == "up":
        return "call"
    if direction == "down":
        return "put"
    return "skip"


def _rag_vote(rag: dict[str, Any]) -> str:
    if not rag.get("snippets") and rag.get("trading_id") is None:
        return "skip"
    return "neutral"


def _rules_trade_decision(votes: list[str]) -> TradeDecision:
    actionable = [v for v in votes if v in ("call", "put", "up", "down")]
    if not actionable:
        return TradeDecision(action="skip", confidence=0.0, reason="no consensus")

    normalized = ["call" if v in ("up", "call") else "put" for v in actionable]
    call_count = normalized.count("call")
    put_count = normalized.count("put")
    if call_count == put_count:
        return TradeDecision(action="skip", confidence=0.3, reason="tie")

    action = "call" if call_count > put_count else "put"
    total = call_count + put_count
    confidence = max(call_count, put_count) / total
    return TradeDecision(action=action, confidence=confidence, reason="rule majority")


def run_rules_decision(
    snapshot: WorkflowSnapshot,
    market: dict[str, Any],
    indicator: dict[str, Any],
    rag: dict[str, Any],
) -> dict[str, Any]:
    _ = snapshot
    votes = [_indicator_vote(indicator), _angle_vote(market), _rag_vote(rag)]
    return rules_decision_to_state_dict(_rules_trade_decision(votes))


def _bedrock_llm() -> LLM | None:
    model_id = (settings.bedrock_decision_model_id or "").strip()
    region = (settings.bedrock_region or settings.aws_region or "us-west-1").strip()
    if not model_id:
        return None

    os.environ.setdefault("AWS_REGION", region)
    os.environ.setdefault("AWS_DEFAULT_REGION", region)

    return LLM(
        model=f"bedrock/{model_id}",
        aws_region_name=region,
        temperature=0.2,
    )


def _parse_crew_result(result: Any) -> TradeDecision | None:
    pydantic = getattr(result, "pydantic", None)
    if isinstance(pydantic, TradeDecision):
        return pydantic

    tasks_output = getattr(result, "tasks_output", None) or []
    for task_output in reversed(tasks_output):
        task_pydantic = getattr(task_output, "pydantic", None)
        if isinstance(task_pydantic, TradeDecision):
            return task_pydantic

    return None


def _run_crewai_decision(
    snapshot: WorkflowSnapshot,
    market: dict[str, Any],
    indicator: dict[str, Any],
    rag: dict[str, Any],
) -> dict[str, Any] | None:
    from crewai import Agent, Crew, Process, Task

    llm = _bedrock_llm()
    if llm is None:
        return None

    context = DecisionContext.build(snapshot, market, indicator, rag)
    agent = Agent(
        role="Trading Analyst",
        goal="Choose call, put, or skip for a short binary-options trade.",
        backstory="Uses indicator, price action, and RAG snippets.",
        llm=llm,
        verbose=False,
    )
    task = Task(
        description=(
            "Review the JSON context and return a trade decision.\n\n"
            f"{context.model_dump_json()}"
        ),
        expected_output="Structured trade decision (action, confidence, reason).",
        agent=agent,
        output_pydantic=TradeDecision,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

    try:
        result = crew.kickoff()
        decision = _parse_crew_result(result)
        if decision is not None:
            return crew_decision_to_state_dict(decision)
        logger.warning("CrewAI returned no structured decision: %s", str(result)[:200])
        return None
    except Exception as exc:
        logger.warning("CrewAI decision failed: %s", exc)
        return None


def run_decision_sync(
    snapshot: WorkflowSnapshot,
    market: dict[str, Any],
    indicator: dict[str, Any],
    rag: dict[str, Any],
) -> dict[str, Any]:
    crew = _run_crewai_decision(snapshot, market, indicator, rag)
    if crew is not None:
        return crew
    return run_rules_decision(snapshot, market, indicator, rag)


async def run_decision(
    snapshot: WorkflowSnapshot,
    market: dict[str, Any],
    indicator: dict[str, Any],
    rag: dict[str, Any],
) -> dict[str, Any]:
    return await asyncio.to_thread(run_decision_sync, snapshot, market, indicator, rag)
