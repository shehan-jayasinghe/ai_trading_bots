from __future__ import annotations

import asyncio
from urllib.parse import quote_plus

from playwright.async_api import BrowserContext, Page

from .config import Settings


DDG_HTML_SEARCH = "https://html.duckduckgo.com/html/?q="


class DuckDuckGoSearch:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(
        self,
        query: str,
        browser_context: BrowserContext,
        scrape_limit: asyncio.Semaphore,
    ) -> str:
        print(f"\nSearching for: {query}")

        async with scrape_limit:
            page = await browser_context.new_page()
            try:
                await self._navigate(page, query)

                if await self._detect_bot_wall(page):
                    return (
                        f"Search query: {query}\n\n"
                        "(DuckDuckGo showed a bot challenge.)"
                    )

                snippets = await self._extract_snippets(page)
                if snippets:
                    return self._format_context(query, snippets)

                return f"Search query: {query}\n\n(No DuckDuckGo snippets extracted.)"
            finally:
                await page.close()

    async def _detect_bot_wall(self, page: Page) -> bool:
        if await page.locator(".anomaly-modal__title").count():
            return True
        if await page.get_by_text("Unfortunately, bots use DuckDuckGo too.").count():
            return True
        return False

    async def _navigate(self, page: Page, query: str) -> None:
        url = f"{DDG_HTML_SEARCH}{quote_plus(query)}"
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)

    async def _extract_snippets(self, page: Page) -> list[str]:
        selectors = (
            ".links_main .result",
            ".web-result",
            "div.results_links",
        )
        for sel in selectors:
            loc = page.locator(sel)
            try:
                await loc.first.wait_for(state="visible", timeout=8_000)
            except Exception:
                continue
            chunks: list[str] = []
            for i in range(await loc.count()):
                if i >= self.settings.search_max_results:
                    break
                text = (await loc.nth(i).inner_text()).strip()
                if text:
                    chunks.append(text[: self.settings.search_results_per_chunk])
            if chunks:
                return chunks
        return []

    def _format_context(self, query: str, snippets: list[str]) -> str:
        body = "\n\n---\n\n".join(snippets)
        if len(body) > self.settings.search_max_chars_total:
            body = body[: self.settings.search_max_chars_total] + "\n... (truncated)"
        return f"Search query: {query}\n\nExtracted snippets:\n\n{body}"
