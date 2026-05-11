from __future__ import annotations

import asyncio

from openai import OpenAI
from playwright.async_api import BrowserContext

from ..schemas import ResearchResult
from ..search import DuckDuckGoSearch


class ResearchAgent:
    def __init__(self, client: OpenAI, model: str, search_tool: DuckDuckGoSearch):
        self.client = client
        self.model = model
        self.search_tool = search_tool

    async def research(
        self,
        topic: str,
        browser_context: BrowserContext,
        scrape_limit: asyncio.Semaphore,
    ) -> str:
        search_data = await self.search_tool.search(topic, browser_context, scrape_limit)

        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a research summarization agent. "
                        "Summarize the provided research data clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": search_data,
                },
            ],
            text_format=ResearchResult,
        )

        result = response.output_parsed

        print(f"\n🧠 Research Summary for '{topic}':")
        print(result.summary)

        return result.summary
