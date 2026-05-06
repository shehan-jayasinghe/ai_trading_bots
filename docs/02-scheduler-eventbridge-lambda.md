# Scheduled Runner (EventBridge + Lambda)

## Purpose
Run trading automation every fixed interval (initially every 2 hours).

## Flow
1. EventBridge rule triggers scheduler Lambda.
2. Lambda starts run via:
   - HTTP call: `POST /runs` (preferred), OR
   - direct invoke shared Python service.
3. API returns `202 Accepted` with `run_id` immediately.
4. Run job is queued (for example SQS) and picked by worker.
5. Worker executes max configured trades (`TRADES_PER_RUN`).
6. Worker persists run/trade state and logs continuously.

## Idempotency
- Use `schedule_trigger_id` to prevent duplicate runs.
- Reject if a run is already active for same symbol/time window.

## Initial Run Policy
- Symbol set: Deriv Tick 10 index (single symbol initially)
- Interval: every 2h
- Trades per run: start small (e.g. 5)
- Cycle policy: e.g. 10-trade MM block

## Failure Handling
- Retry scheduler safely (idempotent)
- Alert on repeated run failures
- Dead-letter queue recommended for failed job messages
