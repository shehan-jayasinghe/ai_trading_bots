# Local environment (Docker)

Postgres + Kafka for local development.

## Prerequisites

- Docker Desktop (or Docker Engine + Compose)

## Setup

1. Copy env file (if you use Postgres from this stack):

   ```bash
   cp .env.example .env
   ```

2. Start services:

   ```bash
   docker compose up -d
   ```

3. Create workflow topics (optional, auto-create may be enabled):

   ```bash
   ./scripts/kafka-init-topics.sh
   ```

## Endpoints

| Service   | URL / address              |
|-----------|----------------------------|
| Postgres  | `localhost:5432` (see `.env`) |
| Kafka (host / API / workers) | `localhost:9092` |
| Kafka (Docker internal)      | `kafka:9094`     |
| Kafka UI                     | http://localhost:8081 |

## Environment files

| File | Purpose |
|------|---------|
| `local-env/.env` | Docker Compose only (`POSTGRES_*`, `KAFKA_HOST_PORT`, `KAFKA_UI_HOST_PORT`) |
| `backend/.env` | API + Kafka publish (`POSTGRES_DATABASE_URL`, `KAFKA_*`) |
| `frontend/.env` | Next.js + Prisma (`DATABASE_URL` — same DB as backend) |
| `workers/.env` | Planner + executor (`KAFKA_BOOTSTRAP_SERVERS`) |

Copy `local-env/.env.example` → `local-env/.env`, then align URLs with your Postgres user/password/db.

Kafka image: `apache/kafka:3.7.2` (official; Bitnami `3.7` is not on public Docker Hub).

## Backend

Set in `backend/.env`:

```env
POSTGRES_DATABASE_URL=postgresql+asyncpg://deriv:deriv@localhost:5432/deriv
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```
