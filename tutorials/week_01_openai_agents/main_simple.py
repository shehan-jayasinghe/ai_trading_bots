from __future__ import annotations

import asyncio
from os import environ
from urllib.parse import quote_plus

from dotenv import load_dotenv
from openai import OpenAI
from playwright.async_api import BrowserContext, Page, async_playwright
from pydantic import BaseModel


load_dotenv()

MODEL = "gpt-4.1"
OPENAI_API_KEY = environ.get("OPENAI_API_KEY")

SEARCH_MAX_RESULTS = 8
SEARCH_MAX_CHARS_TOTAL = 12_000
SEARCH_RESULTS_PER_CHUNK = 800
SCRAPE_CONCURRENCY = 3

DDG_HTML_SEARCH = "https://html.duckduckgo.com/html/?q="
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class ResearchPlan(BaseModel):
    steps: list[str]


class ResearchResult(BaseModel):
    summary: str


async def detect_bot_wall(page: Page) -> bool:
    if await page.locator(".anomaly-modal__title").count():
        return True
    if await page.get_by_text("Unfortunately, bots use DuckDuckGo too.").count():
        return True
    return False


async def open_duckduckgo(page: Page, query: str) -> None:
    url = f"{DDG_HTML_SEARCH}{quote_plus(query)}"
    await page.goto(url, wait_until="domcontentloaded", timeout=60_000)


async def extract_duckduckgo_snippets(page: Page) -> list[str]:
    selectors = (
        ".links_main .result",
        ".web-result",
        "div.results_links",
    )

    for selector in selectors:
        results = page.locator(selector)
        try:
            await results.first.wait_for(state="visible", timeout=8_000)
        except Exception:
            continue

        snippets: list[str] = []
        for index in range(await results.count()):
            if index >= SEARCH_MAX_RESULTS:
                break
            text = (await results.nth(index).inner_text()).strip()
            if text:
                snippets.append(text[:SEARCH_RESULTS_PER_CHUNK])

        if snippets:
            return snippets

    return []


def format_search_context(query: str, snippets: list[str]) -> str:
    body = "\n\n---\n\n".join(snippets)
    if len(body) > SEARCH_MAX_CHARS_TOTAL:
        body = body[:SEARCH_MAX_CHARS_TOTAL] + "\n... (truncated)"
    return f"Search query: {query}\n\nExtracted snippets:\n\n{body}"


async def web_search(
    query: str,
    browser_context: BrowserContext,
    scrape_limit: asyncio.Semaphore,
) -> str:
    print(f"\nSearching for: {query}")

    async with scrape_limit:
        page = await browser_context.new_page()
        try:
            await open_duckduckgo(page, query)

            if await detect_bot_wall(page):
                return f"Search query: {query}\n\n(DuckDuckGo showed a bot challenge.)"

            snippets = await extract_duckduckgo_snippets(page)
            if snippets:
                return format_search_context(query, snippets)

            return f"Search query: {query}\n\n(No DuckDuckGo snippets extracted.)"
        finally:
            await page.close()


async def send_email(content: str) -> str:
    print("\nSending Email...\n")
    await asyncio.sleep(1)
    return f"Email sent successfully.\n\nContent:\n{content}"


async def plan_research(client: OpenAI, task: str) -> list[str]:
    response = client.responses.parse(
        model=MODEL,
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


async def research_topic(
    client: OpenAI,
    topic: str,
    browser_context: BrowserContext,
    scrape_limit: asyncio.Semaphore,
) -> str:
    search_data = await web_search(topic, browser_context, scrape_limit)

    response = client.responses.parse(
        model=MODEL,
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

    print(f"\nResearch Summary for '{topic}':")
    print(result.summary)

    return result.summary


async def run_workflow(task: str) -> str:
    print("\nOPENAI SDK WORKFLOW STARTED")

    client = OpenAI(api_key=OPENAI_API_KEY)
    steps = await plan_research(client, task)

    print("\nPLAN:")
    for index, step in enumerate(steps, start=1):
        print(f"{index}. {step}")

    print("\nRunning parallel research tasks...\n")

    scrape_limit = asyncio.Semaphore(SCRAPE_CONCURRENCY)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        browser_context = await browser.new_context(
            user_agent=BROWSER_USER_AGENT,
            locale="en-US",
        )
        try:
            results = await asyncio.gather(
                *[
                    research_topic(client, step, browser_context, scrape_limit)
                    for step in steps
                ]
            )
        finally:
            await browser.close()

    combined_summary = "\n\n".join(results)
    return await send_email(combined_summary)


async def main() -> None:
    result = await run_workflow("Research AI trends in 2025")

    print("\n==============================")
    print("FINAL RESULT")
    print("==============================\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
