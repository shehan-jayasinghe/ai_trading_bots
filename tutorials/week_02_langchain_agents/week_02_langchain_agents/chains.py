from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .schemas import ResearchPlan, ResearchResult


class PlannerChain:
    def __init__(self, model: ChatOpenAI):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a planning agent. Break the task into short research steps.",
                ),
                ("user", "{task}"),
            ]
        )
        self.chain = prompt | model.with_structured_output(ResearchPlan)

    async def plan(self, task: str) -> list[str]:
        plan = await self.chain.ainvoke({"task": task})
        return plan.steps


class ResearchChain:
    def __init__(self, model: ChatOpenAI):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are a research summarization agent. "
                        "Summarize the provided research data clearly."
                    ),
                ),
                ("user", "{search_data}"),
            ]
        )
        self.chain = prompt | model.with_structured_output(ResearchResult)

    async def summarize(self, search_data: str) -> str:
        result = await self.chain.ainvoke({"search_data": search_data})
        return result.summary
