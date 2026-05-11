from __future__ import annotations

import asyncio

from openai import OpenAI
from playwright.async_api import async_playwright

from .agents import PlannerAgent, ResearchAgent
from .config import Settings
from .search import DuckDuckGoSearch
from .tools import send_email_tool


class ResearchWorkflow:
    def __init__(
        self,
        settings: Settings | None = None,
        client: OpenAI | None = None,
    ):
        self.settings = settings or Settings.from_env()
        self.client = client or OpenAI(api_key=self.settings.openai_api_key)
        self.search_tool = DuckDuckGoSearch(self.settings)
        self.planner = PlannerAgent(self.client, self.settings.model)
        self.researcher = ResearchAgent(
            self.client,
            self.settings.model,
            self.search_tool,
        )

    async def run(self, user_input: str) -> str:
        print("\n🚀 MAIN AGENT STARTED")

        steps = await self.planner.plan(user_input)

        print("\n📋 PLAN:")
        for index, step in enumerate(steps, start=1):
            print(f"{index}. {step}")

        print("\n⚡ Running parallel research tasks (browser context shared)...\n")

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
                        self.researcher.research(step, browser_context, scrape_limit)
                        for step in steps
                    ]
                )
            finally:
                await browser.close()

        combined_summary = "\n\n".join(results)

        return await send_email_tool(combined_summary)
