from __future__ import annotations

import asyncio


async def send_email_tool(content: str) -> str:
    print("\n📧 Sending Email...\n")

    await asyncio.sleep(1)

    return f"✅ Email sent successfully.\n\nContent:\n{content}"
