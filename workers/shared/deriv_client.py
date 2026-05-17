"""Minimal Deriv WebSocket client (authorize + one request)."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import websockets

logger = logging.getLogger(__name__)

DEFAULT_WS_ENDPOINT = "wss://ws.derivws.com/websockets/v3"
DEFAULT_APP_ID = "1089"


def resolve_app_id(app_id: str | None) -> str:
    raw = (app_id or "").strip()
    if raw.isdigit() and int(raw) > 0:
        return raw
    return DEFAULT_APP_ID


async def deriv_request(
    *,
    app_id: str | None,
    token: str,
    payload: dict[str, Any],
    endpoint: str = DEFAULT_WS_ENDPOINT,
    timeout_sec: float = 30.0,
) -> dict[str, Any]:
    """Connect, authorize, send one payload, return matching response."""
    resolved_app = resolve_app_id(app_id)
    url = f"{endpoint}?app_id={resolved_app}"
    auth_req_id = 1
    main_req_id = 2

    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"authorize": token, "req_id": auth_req_id}))
        auth_msg = await _wait_req_id(ws, auth_req_id, timeout_sec)
        if auth_msg.get("error"):
            raise RuntimeError(f"Deriv authorize failed: {auth_msg['error']}")

        body = {**payload, "req_id": main_req_id}
        await ws.send(json.dumps(body))
        return await _wait_req_id(ws, main_req_id, timeout_sec)


async def _wait_req_id(
    ws: websockets.ClientConnection,
    req_id: int,
    timeout_sec: float,
) -> dict[str, Any]:
    deadline = asyncio.get_running_loop().time() + timeout_sec
    while asyncio.get_running_loop().time() < deadline:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout_sec)
        data = json.loads(raw)
        if data.get("req_id") == req_id:
            if data.get("error"):
                raise RuntimeError(f"Deriv API error: {data['error']}")
            return data
    raise TimeoutError(f"Deriv WebSocket timeout waiting for req_id {req_id}")


async def fetch_ticks_history(
    *,
    app_id: str | None,
    token: str,
    symbol: str,
    count: int = 100,
) -> dict[str, Any]:
    resp = await deriv_request(
        app_id=app_id,
        token=token,
        payload={
            "ticks_history": symbol,
            "style": "ticks",
            "count": count,
            "end": "latest",
        },
    )
    history = resp.get("history") or {}
    prices = history.get("prices") or []
    times = history.get("times") or []
    ticks = [
        {"epoch": int(times[i]), "price": float(prices[i])}
        for i in range(min(len(prices), len(times)))
    ]
    return {
        "symbol": symbol,
        "ticks": ticks,
        "last": float(prices[-1]) if prices else None,
        "prices": [float(p) for p in prices],
    }


async def place_rise_fall_trade(
    *,
    app_id: str | None,
    token: str,
    symbol: str,
    direction: str,
    stake: float,
    duration: int = 2,
    duration_unit: str = "t",
    currency: str = "USD",
) -> dict[str, Any]:
    contract_type = "CALL" if direction.lower() in ("call", "rise", "up") else "PUT"
    proposal = await deriv_request(
        app_id=app_id,
        token=token,
        payload={
            "proposal": 1,
            "amount": stake,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": currency,
            "duration": duration,
            "duration_unit": duration_unit,
            "symbol": symbol,
        },
    )
    proposal_id = (proposal.get("proposal") or {}).get("id")
    ask_price = (proposal.get("proposal") or {}).get("ask_price")
    if not proposal_id or ask_price is None:
        raise RuntimeError("Deriv proposal missing id or ask_price")

    buy = await deriv_request(
        app_id=app_id,
        token=token,
        payload={"buy": proposal_id, "price": float(ask_price)},
    )
    contract_id = (buy.get("buy") or {}).get("contract_id")
    return {
        "contract_id": contract_id,
        "proposal_id": proposal_id,
        "contract_type": contract_type,
        "stake": stake,
        "ask_price": float(ask_price),
        "symbol": symbol,
        "direction": direction,
    }
