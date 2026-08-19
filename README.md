# AI Trading Bots Platform

A modular trading platform repository organized around a FastAPI backend, frontend, worker services, infrastructure, deployment configuration, and supporting documentation.

## Architecture

```text
                    AI Trading Bots Platform
                              |
        +---------------------+---------------------+
        |                     |                     |
     Frontend              Backend               Workers
        |                     |                     |
        |              FastAPI / Python            |
        |                     |                     |
        |          +----------+----------+          |
        |          |                     |          |
        |      PostgreSQL            Kafka <--------+
        |          |                     |
        +----------+---------------------+
                              |
                   Infrastructure / Deploy
```

## Repository Structure

- `backend/` — FastAPI backend application.
- `frontend/` — user interface.
- `workers/` — background processing services.
- `worker_factory/` — worker orchestration/support.
- `infrastructure/` — infrastructure configuration.
- `deploy/` — deployment resources.
- `jenkins/` — CI/CD resources.
- `docs/` — project documentation.
- `tutorials/` — supporting tutorials.

## Backend Stack

The backend targets Python 3.11+ and uses:

- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL (`asyncpg` / `psycopg2`)
- PyJWT and Cryptography
- `aiokafka` for Kafka integration

## Runtime Flow

1. A client sends a request to the FastAPI backend.
2. Authentication and request validation are applied.
3. Application services process the request.
4. PostgreSQL is used for relational persistence where required.
5. Kafka is used for asynchronous/event-driven communication.
6. Background workers process long-running or asynchronous tasks.
7. Infrastructure and deployment resources provide the runtime environment.

## Local Development

From the backend directory, install the dependencies defined by the project configuration and start the FastAPI application with Uvicorn.

```bash
cd backend
uvicorn app.main:app --reload
```

> The exact application module and required environment variables should be verified against the current backend configuration before running in a new environment.

## Configuration & Security

Use the provided `.env.example` as the starting point for local configuration. Never commit API tokens, database passwords, JWT secrets, broker credentials, or other production secrets.

For production, use a proper secret-management solution and environment-specific configuration.

## Deployment

Deployment and infrastructure concerns are intentionally separated from application code through the `deploy/`, `infrastructure/`, and `jenkins/` directories.

## Disclaimer

Trading systems can result in financial loss. This repository is software infrastructure and experimentation; trading strategies and risk controls should be independently validated before any real-money use.
