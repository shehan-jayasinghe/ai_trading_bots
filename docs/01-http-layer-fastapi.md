# HTTP Layer (FastAPI)

## Purpose
Expose operational APIs for runs, trades, health, and internal debugging.

## Core Endpoints
- `GET /health` - service alive
- `GET /ready` - dependencies ready (DB/vector/model checks)
- `POST /runs` - enqueue one bot run, return immediately (`202 Accepted`)
- `GET /runs/{run_id}` - run status
- `GET /trades` - list trades with filters
- `GET /trades/{trade_id}/card` - full trade card (pre/post windows, indicators, MM, model decisions)

## Deployment Options
- Read API on Lambda + API Gateway (good for low/medium read traffic), or FastAPI on ECS/Fargate
- Worker execution on ECS/Fargate jobs (recommended for multi-step trade runs)
- Lambda + API Gateway + Mangum (optional for lightweight API-only setup)

## Security
- API auth required (JWT/API key/IAM)
- Never return secrets in errors
- Rate limit admin endpoints

## Notes
- Keep HTTP thin; business logic in shared service layer.
- `POST /runs` should not block until all trades finish.
- Return `run_id` and `status=queued`; worker updates progress in DB.
- Same service methods should be callable by scheduler Lambda and worker jobs.
