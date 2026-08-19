# AI Trading Bots Platform

A modular platform for experimenting with AI-assisted trading workflows, backend APIs, worker services, event-driven processing, and deployment infrastructure.

## Highlights

- FastAPI backend and Python services
- Event-driven processing with Kafka
- PostgreSQL persistence
- Frontend and background worker components
- Docker, deployment, and CI/CD configuration
- Supporting architecture and development documentation

## Architecture

```text
Client -> Frontend -> FastAPI Backend -> PostgreSQL
                         |
                         v
                       Kafka
                         |
                  Background Workers
                         |
                  Deployment / Infra
```

## Repository Structure

- `backend/` — API and application services
- `frontend/` — web interface
- `workers/` — asynchronous processing
- `worker_factory/` — worker orchestration
- `infrastructure/` — infrastructure configuration
- `deploy/` — deployment resources
- `jenkins/` — CI/CD resources
- `docs/` — architecture and project documentation

## Local Development

Install the backend dependencies and start the API with the project's configured environment:

```bash
cd backend
uvicorn app.main:app --reload
```

Verify the exact module and environment variables against the current project configuration before running.

## Security

Keep API tokens, database credentials, broker credentials, JWT secrets, and other sensitive values in environment variables or a secret manager. Never commit production secrets.

## Status

This repository is an engineering and experimentation platform for AI-assisted, event-driven trading workflows. Validate strategies and risk controls independently before any real-money use.
