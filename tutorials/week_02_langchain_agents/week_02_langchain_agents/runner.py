from __future__ import annotations

import asyncio

from .workflow import LangChainResearchWorkflow


async def run() -> None:
    workflow = LangChainResearchWorkflow()
    result = await workflow.run("Research AI trends in 2025")

    print("\n==============================")
    print("FINAL RESULT")
    print("==============================\n")

    print(result)


def main() -> None:
    asyncio.run(run())
