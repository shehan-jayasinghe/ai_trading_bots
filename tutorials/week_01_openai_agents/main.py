from __future__ import annotations

import asyncio
from os import environ
from urllib.parse import quote_plus

from dotenv import load_dotenv
from openai import OpenAI
from playwright.async_api import BrowserContext, async_playwright
from pydantic import BaseModel

load_dotenv()

# ---------------------------------
# OpenAI Client
# ---------------------------------
OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Scraping caps (keep prompts bounded)
SEARCH_MAX_RESULTS = 8
SEARCH_MAX_CHARS_TOTAL = 12_000
SEARCH_RESULTS_PER_CHUNK = 800

DDG_HTML_SEARCH = "https://html.duckduckgo.com/html/?q="
WIKI_SPECIAL_SEARCH = "https://en.wikipedia.org/wiki/Special:Search?search="

# ---------------------------------
# 1. Structured Output Schemas
# ---------------------------------


class ResearchPlan(BaseModel):
    steps: list[str]


class ResearchResult(BaseModel):
    summary: str


# ---------------------------------
# 2. Playwright web search tool (multi-step)
# ---------------------------------


async def _step_detect_bot_wall(page) -> bool:
    if await page.locator(".anomaly-modal__title").count():
        return True
    if await page.get_by_text("Unfortunately, bots use DuckDuckGo too.").count():
        return True
    return False


async def _step_navigate_ddg(page, query: str) -> None:
    url = f"{DDG_HTML_SEARCH}{quote_plus(query)}"
    await page.goto(url, wait_until="domcontentloaded", timeout=60_000)


async def _step_extract_ddg_snippets(page) -> list[str]:
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
            if i >= SEARCH_MAX_RESULTS:
                break
            text = (await loc.nth(i).inner_text()).strip()
            if text:
                chunks.append(text[:SEARCH_RESULTS_PER_CHUNK])
        if chunks:
            return chunks
    return []


async def _step_navigate_wikipedia_search(page, query: str) -> None:
    url = f"{WIKI_SPECIAL_SEARCH}{quote_plus(query)}"
    await page.goto(url, wait_until="domcontentloaded", timeout=60_000)


async def _step_extract_wikipedia_search_page(page) -> list[str]:
    loc = page.locator(".mw-search-result")
    try:
        await loc.first.wait_for(state="visible", timeout=15_000)
    except Exception:
        pass

    chunks: list[str] = []
    n = min(await loc.count(), SEARCH_MAX_RESULTS)
    for i in range(n):
        text = (await loc.nth(i).inner_text()).strip()
        if text:
            chunks.append(text[:SEARCH_RESULTS_PER_CHUNK])

    if chunks:
        return chunks

    alt = page.locator("#mw-content-text .mw-parser-output")
    if await alt.count():
        text = (await alt.first.inner_text()).strip()
        if text:
            return [text[:SEARCH_RESULTS_PER_CHUNK]]

    body = (await page.inner_text("body")).strip()
    return [body[:SEARCH_RESULTS_PER_CHUNK]] if body else []


def _step_format_context(query: str, snippets: list[str]) -> str:
    body = "\n\n---\n\n".join(snippets)
    if len(body) > SEARCH_MAX_CHARS_TOTAL:
        body = body[:SEARCH_MAX_CHARS_TOTAL] + "\n… (truncated)"
    return f"Search query: {query}\n\nExtracted snippets:\n\n{body}"


async def web_search_tool(
    query: str,
    browser_context: BrowserContext,
    scrape_limit: asyncio.Semaphore,
) -> str:
    """
    Headless search pipeline:
      1) Open a tab
      2) Open DuckDuckGo HTML SERP
      3) If anti-bot UI blocks, switch to Wikipedia search
      4) Else extract snippets; if empty, Wikipedia fallback
      5) Close the tab (always)
    """

    print(f"\n🔍 Searching for: {query}")

    async with scrape_limit:
        page = await browser_context.new_page()
        try:
            await _step_navigate_ddg(page, query)

            if await _step_detect_bot_wall(page):
                print("  DuckDuckGo showed a challenge → falling back to Wikipedia search.")
                await _step_navigate_wikipedia_search(page, query)
                snippets = await _step_extract_wikipedia_search_page(page)
                if not snippets:
                    return (
                        f"Search query: {query}\n\n"
                        "(No snippets extracted after Wikipedia fallback.)"
                    )
                return _step_format_context(query, snippets)

            snippets = await _step_extract_ddg_snippets(page)
            if snippets:
                return _step_format_context(query, snippets)

            print("  No DDG snippets → Wikipedia search fallback.")
            await _step_navigate_wikipedia_search(page, query)
            snippets = await _step_extract_wikipedia_search_page(page)
            if not snippets:
                return (
                    f"Search query: {query}\n\n"
                    "(No snippets extracted from DDG or Wikipedia.)"
                )
            return _step_format_context(query, snippets)

        finally:
            await page.close()


# ---------------------------------
# 3. Other tools
# ---------------------------------


async def send_email_tool(content: str) -> str:
    print("\n📧 Sending Email...\n")

    await asyncio.sleep(1)

    return f"✅ Email sent successfully.\n\nContent:\n{content}"


# ---------------------------------
# 4. Research Agent (Sub-Agent)
# ---------------------------------


async def research_agent(
    topic: str,
    browser_context: BrowserContext,
    scrape_limit: asyncio.Semaphore,
) -> str:

    search_data = await web_search_tool(topic, browser_context, scrape_limit)

    response = client.responses.parse(
        model="gpt-4.1",
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


# ---------------------------------
# 5. Planner Agent
# ---------------------------------


async def planner_agent(task: str) -> list[str]:

    response = client.responses.parse(
        model="gpt-4.1",
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


# ---------------------------------
# 6. Main Agent (Orchestrator)
# ---------------------------------


async def main_agent(user_input: str):

    print("\n🚀 MAIN AGENT STARTED")

    steps = await planner_agent(user_input)

    print("\n📋 PLAN:")
    for index, step in enumerate(steps, start=1):
        print(f"{index}. {step}")

    print("\n⚡ Running parallel research tasks (browser context shared)...\n")

    scrape_limit = asyncio.Semaphore(3)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        browser_context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        try:
            results = await asyncio.gather(
                *[
                    research_agent(step, browser_context, scrape_limit)
                    for step in steps
                ]
            )
        finally:
            await browser.close()

    combined_summary = "\n\n".join(results)

    email_result = await send_email_tool(combined_summary)

    return email_result


# ---------------------------------
# 7. Runner
# ---------------------------------


async def run():

    result = await main_agent("Research AI trends in 2025")

    print("\n==============================")
    print("FINAL RESULT")
    print("==============================\n")

    print(result)


# ---------------------------------
# Application Entry Point
# ---------------------------------

if __name__ == "__main__":
    asyncio.run(run())
