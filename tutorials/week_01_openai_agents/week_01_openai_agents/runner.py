from __future__ import annotations

import asyncio

from .workflow import ResearchWorkflow


async def run() -> None:
    workflow = ResearchWorkflow()
    result = await workflow.run("Research AI trends in 2025")

    print("\n==============================")
    print("FINAL RESULT")
    print("==============================\n")

    print(result)


def main() -> None:
    asyncio.run(run())
