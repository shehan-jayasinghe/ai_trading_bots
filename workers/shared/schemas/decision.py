from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

from shared.events import WorkflowSnapshot
from shared.settings import settings


class TradeDecision(BaseModel):
    """CrewAI structured output and rules fallback."""

    model_config = ConfigDict(extra="ignore")

    action: Literal["call", "put", "skip"] = "skip"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = ""

    @field_validator("action", mode="before")
    @classmethod
    def _normalize_action(cls, value: Any) -> str:
        action = str(value or "skip").lower()
        return action if action in ("call", "put", "skip") else "skip"

    @field_validator("confidence", mode="before")
    @classmethod
    def _normalize_confidence(cls, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0


class RagSnippet(BaseModel):
    model_config = ConfigDict(extra="ignore")

    trade_id: str | None = None
    text: str | None = None
    outcome: str | None = None
    source: str | None = None


class RagContext(BaseModel):
    model_config = ConfigDict(extra="ignore")

    trading_id: str | None = None
    snippets: list[RagSnippet] = Field(default_factory=list)
    exact_count: int = 0
    semantic_count: int = 0

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Self:
        snippets = [
            RagSnippet.model_validate(item)
            for item in payload.get("snippets") or []
            if isinstance(item, dict)
        ]
        return cls(
            trading_id=payload.get("trading_id"),
            snippets=snippets,
            exact_count=int(payload.get("exact_count") or 0),
            semantic_count=int(payload.get("semantic_count") or 0),
        )


class DecisionContext(BaseModel):
    """Input bundle passed to the CrewAI decision task."""

    workflow: str
    symbol: str
    market: dict[str, Any] = Field(default_factory=dict)
    indicator: dict[str, Any] = Field(default_factory=dict)
    rag: RagContext = Field(default_factory=RagContext)

    @classmethod
    def build(
        cls,
        snapshot: WorkflowSnapshot,
        market: dict[str, Any],
        indicator: dict[str, Any],
        rag: dict[str, Any],
    ) -> Self:
        return cls(
            workflow=snapshot.name,
            symbol=snapshot.trading_pair,
            market=market,
            indicator=indicator,
            rag=RagContext.from_payload(rag),
        )


def decision_to_state_dict(
    decision: TradeDecision,
    *,
    provider: str,
    model: str | None = None,
) -> dict[str, Any]:
    payload = decision.model_dump()
    payload["provider"] = provider
    if model:
        payload["model"] = model
    return payload


def crew_decision_to_state_dict(decision: TradeDecision) -> dict[str, Any]:
    return decision_to_state_dict(
        decision,
        provider="crewai+bedrock",
        model=settings.bedrock_decision_model_id or None,
    )


def rules_decision_to_state_dict(decision: TradeDecision) -> dict[str, Any]:
    return decision_to_state_dict(decision, provider="rules")
