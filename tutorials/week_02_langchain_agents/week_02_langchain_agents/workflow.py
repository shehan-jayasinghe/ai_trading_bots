from __future__ import annotations

import asyncio
from typing import Any

from langchain_openai import ChatOpenAI
from playwright.async_api import BrowserContext, async_playwright

from .chains import PlannerChain, ResearchChain
from .config import Settings
from .search import DuckDuckGoSearch
from .tools import send_email_tool


class LangChainResearchWorkflow:
    def __init__(
        self,
        settings: Settings | None = None,
        model: ChatOpenAI | None = None,
    ):
        self.settings = settings or Settings.from_env()
        self.model = model or self._build_model()
        self.search_tool = DuckDuckGoSearch(self.settings)
        self.planner = PlannerChain(self.model)
        self.researcher = ResearchChain(self.model)

    def _build_model(self) -> ChatOpenAI:
        model_kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "temperature": self.settings.temperature,
        }
        if self.settings.openai_api_key:
            model_kwargs["api_key"] = self.settings.openai_api_key
        return ChatOpenAI(**model_kwargs)

    async def run(self, user_input: str) -> str:
        print("\nLANGCHAIN WORKFLOW STARTED")

        steps = await self.planner.plan(user_input)

        print("\nPLAN:")
        for index, step in enumerate(steps, start=1):
            print(f"{index}. {step}")

        print("\nRunning parallel research tasks with LangChain chains...\n")

        scrape_limit = asyncio.Semaphore(self.settings.scrape_concurrency)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.settings.browser_headless)
            browser_context = await browser.new_context(
                user_agent=self.settings.browser_user_agent,
                locale=self.settings.browser_locale,
            )
            try:
                results = await asyncio.gather(
                    *[
                        self._research_step(step, browser_context, scrape_limit)
                        for step in steps
                    ]
                )
            finally:
                await browser.close()

        combined_summary = "\n\n".join(results)

        return await send_email_tool(combined_summary)

    async def _research_step(
        self,
        topic: str,
        browser_context: BrowserContext,
        scrape_limit: asyncio.Semaphore,
    ) -> str:
        search_data = await self.search_tool.search(topic, browser_context, scrape_limit)
        summary = await self.researcher.summarize(search_data)

        print(f"\nResearch Summary for '{topic}':")
        print(summary)

        return summary
