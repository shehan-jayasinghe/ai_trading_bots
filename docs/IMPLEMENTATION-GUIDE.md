# Implementation guide: Kafka + LangGraph + CrewAI

End-to-end path from **Run** in FastAPI to daily planner → trade agent chain.

## Is this the best approach?

| Choice | Verdict | Why |
|--------|---------|-----|
| **Kafka** between API and workers | Yes for your scale | API stays fast; planner/executor scale separately; replay + DLQ later |
| **LangGraph** for one trade attempt | Yes | Clear steps, `skip` branch, easy to test without 8 microservices on day one |
| **CrewAI + Bedrock** for decision | Yes (with fallback) | CrewAI uses `BEDROCK_DECISION_MODEL_ID`; **rules** if Bedrock/CrewAI fails |
| **In-process graph first** | Yes (Phase 1) | Split each node to its own Kafka consumer only when you need independent scale |
| **In-memory planner schedule** | Dev only | Replace with Postgres `Schedule` before production |

**Not recommended early:** one Kafka topic per LLM call; running CrewAI on every tick; blocking FastAPI until trades finish.

## Architecture

```
FastAPI (Run) ──► workflow.scheduled ──► Planner ──► workflow.execute ──► Executor (LangGraph)
                                                                              │
                    data → indicator → rag → decision → mm → trade → rag_write
```

## Repo layout

```text
workers/          # Run separately: planner + executor
backend/app/messaging/   # Kafka publish on Run (optional via KAFKA_ENABLED)
docs/IMPLEMENTATION-GUIDE.md   # This file
```

## Prerequisites

```bash
cd local-env && docker compose up -d
./scripts/kafka-init-topics.sh
```

## Environment

**Backend** (`backend/.env`):

```env
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

**Workers** (`workers/.env` — copy from `workers/.env.example`):

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
BEDROCK_DECISION_MODEL_ID=amazon.nova-micro-v1:0
BEDROCK_REGION=us-west-1
# SageMaker + S3 Vectors for RAG — see workers/.env.example
```

## Step-by-step

### 1. Install worker dependencies

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
cd workers
uv sync
cp .env.example .env
export PYTHONPATH=.
```

### 2. Start Kafka consumers (two terminals)

```bash
# Terminal A — planner
uv run python -m planner.main

# Terminal B — executor (LangGraph trade loop)
uv run python -m executor.main
```

### 3. Enable Kafka on API

Set `KAFKA_ENABLED=true` in `backend/.env`, run `cd backend && uv sync`, restart FastAPI.

### 4. Run a workflow from UI

Click **Run** → API sets `status=run` and publishes `workflow.scheduled`.

Planner registers the schedule; at `starting_time` (checked every 30s in dev) it publishes `workflow.execute`.

Executor runs up to `one_day_minimum_trade` trade attempts per day.

### 5. Manual test (skip planner clock)

```bash
cd workers && export PYTHONPATH=. && uv run python scripts/publish_execute_test.py
```

### 6. Next milestones (you implement)

1. Postgres tables: `Schedule`, `Run`, `Trade`, `UserCapital`
2. Planner reads/writes `Schedule` instead of in-memory dict
3. Deriv WebSocket in `executor/agents/data.py` and `trading.py`
4. RAG in `executor/agents/rag.py` — Postgres exact window + S3 Vectors semantic (SageMaker embed; LlamaIndex embedding adapter)
5. Workflow JSON for user “bots” → rules in `decision_crew.py`
6. Split LangGraph nodes to Kafka topics per agent (scale-out)

## Framework roles

| Layer | Tool |
|-------|------|
| Schedule + fire | Kafka + `planner` |
| One trade pipeline | **LangGraph** (`executor/graph.py`) |
| Multi-bot vote | **Rules** + optional **CrewAI** |
| API trigger | FastAPI + `app/messaging/kafka_publisher.py` |

## Troubleshooting

- **No messages**: `KAFKA_ENABLED=true`? Topics created? `docker ps` shows `deriv-kafka-local` healthy?
- **Decision**: CrewAI + Bedrock (`BEDROCK_DECISION_MODEL_ID`); falls back to rules if CrewAI fails
- **Bedrock slow/fails**: enable model in Bedrock console; workers IRSA needs Bedrock access on that model
- **Planner never fires**: `starting_time` must fall in the 30s tick window (UTC in dev); use `publish_execute_test.py` to test executor first
