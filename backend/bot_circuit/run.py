import importlib
import json
from datetime import datetime, timezone
from typing import Any, Callable

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

from bot_circuit.config import settings


def _resolve_callable(path: str) -> Callable[..., dict[str, Any]]:
    if ":" not in path:
        raise ValueError(f"Invalid callable path '{path}'. Expected module:function")
    module_name, fn_name = path.split(":", 1)
    module = importlib.import_module(module_name)
    fn = getattr(module, fn_name, None)
    if fn is None or not callable(fn):
        raise ValueError(f"Callable '{fn_name}' not found in module '{module_name}'")
    return fn


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _call_with_retry(fn: Callable[..., dict[str, Any]], *args: Any) -> dict[str, Any]:
    return fn(*args)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    load_dotenv(override=False)

    data_fn = _resolve_callable(settings.bot_data_fn)
    strategy_fn = _resolve_callable(settings.bot_strategy_fn)
    decision_fn = _resolve_callable(settings.bot_decision_fn)
    execution_fn = _resolve_callable(settings.bot_execution_fn)

    settle_fn = _resolve_callable(settings.bot_settle_fn) if settings.bot_settle_fn else None
    guardrail_fn = _resolve_callable(settings.bot_guardrail_fn) if settings.bot_guardrail_fn else None

    ctx: dict[str, Any] = {
        "run_id": settings.run_id,
        "symbol": settings.deriv_symbol,
        "started_at": _now_iso(),
        "trades_target": settings.trades_per_run,
        "trades_done": 0,
        "history": [],
    }

    print(json.dumps({"event": "run_started", "run_id": settings.run_id, "symbol": settings.deriv_symbol}))

    for idx in range(1, settings.trades_per_run + 1):
        if guardrail_fn:
            guardrail = _call_with_retry(guardrail_fn, ctx)
            if not guardrail.get("allow", True):
                print(json.dumps({"event": "run_stopped_guardrail", "index": idx, "reason": guardrail.get("reason")}))
                break

        data = _call_with_retry(data_fn, ctx)
        signal = _call_with_retry(strategy_fn, ctx, data)
        decision = _call_with_retry(decision_fn, ctx, data, signal)

        if decision.get("action") == "skip":
            ctx["history"].append({"index": idx, "status": "skipped", "decision": decision})
            print(json.dumps({"event": "trade_skipped", "index": idx, "decision": decision}))
            continue

        execution = _call_with_retry(execution_fn, ctx, decision)
        result = _call_with_retry(settle_fn, ctx, execution) if settle_fn else execution

        ctx["trades_done"] += 1
        ctx["history"].append({"index": idx, "status": "done", "decision": decision, "result": result})
        print(json.dumps({"event": "trade_done", "index": idx, "result": result}))

    ctx["ended_at"] = _now_iso()
    print(
        json.dumps(
            {
                "event": "run_finished",
                "run_id": ctx["run_id"],
                "trades_done": ctx["trades_done"],
                "trades_target": ctx["trades_target"],
            }
        )
    )


if __name__ == "__main__":
    main()

