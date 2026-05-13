from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    steps: list[str] = Field(
        description="Short research steps that can run independently."
    )


class ResearchResult(BaseModel):
    summary: str = Field(description="Clear summary of the provided research data.")
