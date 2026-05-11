"""Minimal callables for local smoke tests. Replace with real bot modules in production."""

from typing import Any


def run_data(ctx: dict[str, Any]) -> dict[str, Any]:
    return {"symbol": ctx.get("symbol"), "sample": True}


def run_strategy(ctx: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    return {"bias": "neutral"}


def run_decision(
    ctx: dict[str, Any], data: dict[str, Any], signal: dict[str, Any]
) -> dict[str, Any]:
    return {"action": "skip", "reason": "stub_local"}


def run_execution(ctx: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    return {"status": "not_executed_stub"}
