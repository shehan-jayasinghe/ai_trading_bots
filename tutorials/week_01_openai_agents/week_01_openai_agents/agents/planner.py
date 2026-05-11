from __future__ import annotations

from openai import OpenAI

from ..schemas import ResearchPlan


class PlannerAgent:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    async def plan(self, task: str) -> list[str]:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a planning agent. "
                        "Break the task into short research steps."
                    ),
                },
                {
                    "role": "user",
                    "content": task,
                },
            ],
            text_format=ResearchPlan,
        )

        plan = response.output_parsed
        return plan.steps
