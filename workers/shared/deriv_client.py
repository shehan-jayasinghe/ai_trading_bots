"""Deriv WebSocket client (authorize + request; proposal+buy on one session)."""
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


def _ws_url(app_id: str | None, endpoint: str = DEFAULT_WS_ENDPOINT) -> str:
    return f"{endpoint}?app_id={resolve_app_id(app_id)}"


async def _wait_req_id(
    ws: websockets.ClientConnection,
    req_id: int,
    timeout_sec: float,
) -> dict[str, Any]:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout_sec
    while loop.time() < deadline:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout_sec)
        data = json.loads(raw)
        if data.get("req_id") == req_id:
            if data.get("error"):
                raise RuntimeError(f"Deriv API error: {data['error']}")
            return data
    raise TimeoutError(f"Deriv WebSocket timeout waiting for req_id {req_id}")


async def _authorize(
    ws: websockets.ClientConnection,
    token: str,
    req_id: int,
    timeout_sec: float,
) -> dict[str, Any]:
    await ws.send(json.dumps({"authorize": token, "req_id": req_id}))
    auth_msg = await _wait_req_id(ws, req_id, timeout_sec)
    if auth_msg.get("error"):
        raise RuntimeError(f"Deriv authorize failed: {auth_msg['error']}")
    return auth_msg


async def _request_on_ws(
    ws: websockets.ClientConnection,
    req_id: int,
    payload: dict[str, Any],
    timeout_sec: float,
) -> dict[str, Any]:
    body = {**payload, "req_id": req_id}
    await ws.send(json.dumps(body))
    return await _wait_req_id(ws, req_id, timeout_sec)


async def deriv_request(
    *,
    app_id: str | None,
    token: str,
    payload: dict[str, Any],
    endpoint: str = DEFAULT_WS_ENDPOINT,
    timeout_sec: float = 30.0,
) -> dict[str, Any]:
    """Connect, authorize, send one payload, return matching response."""
    url = _ws_url(app_id, endpoint)
    async with websockets.connect(url) as ws:
        await _authorize(ws, token, 1, timeout_sec)
        return await _request_on_ws(ws, 2, payload, timeout_sec)


async def fetch_ticks_history(
    *,
    app_id: str | None,
    token: str,
    symbol: str,
    count: int = 100,
    endpoint: str = DEFAULT_WS_ENDPOINT,
    timeout_sec: float = 30.0,
) -> dict[str, Any]:
    resp = await deriv_request(
        app_id=app_id,
        token=token,
        endpoint=endpoint,
        timeout_sec=timeout_sec,
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
    contract_strategy: str = "rise_fall",
    endpoint: str = DEFAULT_WS_ENDPOINT,
    timeout_sec: float = 30.0,
) -> dict[str, Any]:
    """Proposal then buy on the same WebSocket session (matches deriv_bot_ai)."""
    if contract_strategy != "rise_fall":
        raise ValueError(f"Unsupported contract strategy: {contract_strategy}")

    contract_type = "CALL" if direction.lower() in ("call", "rise", "up") else "PUT"
    amount = round(float(stake), 2)
    url = _ws_url(app_id, endpoint)

    async with websockets.connect(url) as ws:
        await _authorize(ws, token, 1, timeout_sec)

        proposal = await _request_on_ws(
            ws,
            2,
            {
                "proposal": 1,
                "amount": amount,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": currency.upper(),
                "duration": int(duration),
                "duration_unit": duration_unit,
                "symbol": symbol,
            },
            timeout_sec,
        )
        proposal_id = (proposal.get("proposal") or {}).get("id")
        ask_price = (proposal.get("proposal") or {}).get("ask_price")
        if not proposal_id or ask_price is None:
            raise RuntimeError("Deriv proposal missing id or ask_price")

        logger.info(
            "Deriv proposal ok symbol=%s type=%s stake=%s ask_price=%s",
            symbol,
            contract_type,
            amount,
            ask_price,
        )

        buy = await _request_on_ws(
            ws,
            3,
            {"buy": proposal_id, "price": float(ask_price)},
            timeout_sec,
        )
        contract_id = (buy.get("buy") or {}).get("contract_id")
        logger.info("Deriv buy ok contract_id=%s", contract_id)

        return {
            "contract_id": contract_id,
            "proposal_id": proposal_id,
            "contract_type": contract_type,
            "stake": amount,
            "ask_price": float(ask_price),
            "symbol": symbol,
            "direction": direction,
        }
