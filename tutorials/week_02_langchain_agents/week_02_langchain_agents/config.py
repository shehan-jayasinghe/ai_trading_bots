from __future__ import annotations

from dataclasses import dataclass
from os import environ

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    model: str = "gpt-4.1"
    temperature: float = 0.0
    search_max_results: int = 8
    search_max_chars_total: int = 12_000
    search_results_per_chunk: int = 800
    scrape_concurrency: int = 3
    browser_headless: bool = False
    browser_locale: str = "en-US"
    browser_user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(openai_api_key=environ.get("OPENAI_API_KEY"))
