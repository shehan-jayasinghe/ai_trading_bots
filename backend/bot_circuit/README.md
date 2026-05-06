# Bot Circuit Runner

This folder provides a minimal job runner for the trading bot circuit.
It does not implement new bots. Instead, it calls existing bot functions
configured via environment variables.

## What this does

- Runs a loop for `TRADES_PER_RUN` (for example 5 or 10).
- Calls existing bot steps in order (data, strategy, decision, execution, settle).
- Stops on optional guardrail response or errors.
- Prints run progress to stdout (for scheduler/job logs).

## Required function contracts

Each configured function path should point to a Python callable.
Use `module.submodule:function_name` format.

- `BOT_DATA_FN`:
  - Input: `(ctx: dict) -> dict`
- `BOT_STRATEGY_FN`:
  - Input: `(ctx: dict, data: dict) -> dict`
- `BOT_DECISION_FN`:
  - Input: `(ctx: dict, data: dict, signal: dict) -> dict`
  - Output should include `action` (`call`/`put`/`skip`)
- `BOT_EXECUTION_FN`:
  - Input: `(ctx: dict, decision: dict) -> dict`
  - Output should include `status`
- `BOT_SETTLE_FN` (optional):
  - Input: `(ctx: dict, execution: dict) -> dict`
- `BOT_GUARDRAIL_FN` (optional):
  - Input: `(ctx: dict) -> dict` with `allow` key

## Quick start

1. Create a virtual environment and install dependencies.
2. Set environment variables in `.env`.
3. Run:

```bash
python -m bot_circuit.run
```

## Example env

```env
TRADES_PER_RUN=5
RUN_ID=manual-local-001
DERIV_SYMBOL=R_10
BOT_DATA_FN=your_pkg.data_bot:run
BOT_STRATEGY_FN=your_pkg.strategy_bot:run
BOT_DECISION_FN=your_pkg.decision_bot:run
BOT_EXECUTION_FN=your_pkg.execution_bot:run
BOT_SETTLE_FN=your_pkg.settle_bot:run
```

