from __future__ import annotations

from pydantic import BaseModel


class ResearchPlan(BaseModel):
    steps: list[str]


class ResearchResult(BaseModel):
    summary: str
