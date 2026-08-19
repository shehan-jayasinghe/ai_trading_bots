# AI Trading Bots Platform

## Overview

A multi-part trading platform repository organized around a Python backend, frontend, infrastructure/deployment configuration, worker services, and supporting documentation. The backend project is a FastAPI-based Deriv AI service with PostgreSQL connectivity, JWT/cryptography support, and Kafka integration.

## Repository Architecture

```text
ai_trading_bots/
├── backend/          # Python/FastAPI application
├── frontend/         # User interface
├── workers/          # Background worker processes
├── worker_factory/   # Worker creation/orchestration support
├── infrastructure/   # Infrastructure configuration
├── deploy/            # Deployment resources
├── jenkins/           # CI/CD resources
├── local-env/         # Local environment configuration
├── docs/              # Project documentation
└── tutorials/         # Supporting tutorials/examples
```

## Backend

The backend is a Python 3.11+ application named `deriv-backend`. Its declared dependencies include:

- FastAPI
- Uvicorn
- PyJWT
- Cryptography
- Pydantic
- SQLAlchemy
- asyncpg / psycopg2
- python-multipart
- aiokafka

This indicates an API service with authentication/security, relational persistence, and event-streaming capabilities.

## Data and Messaging

The backend supports PostgreSQL access through SQLAlchemy and both async and synchronous PostgreSQL drivers. Kafka integration is provided through `aiokafka`, allowing backend components to publish or consume events asynchronously.

## Configuration

The backend contains an `.env.example` file. Keep environment-specific secrets and credentials outside source control and configure local values through environment variables.

## Running the Backend

From the backend directory, install the Python dependencies and run the FastAPI application with Uvicorn. The exact application module and environment requirements should be taken from the current backend configuration before deployment.

## Deployment and Operations

The repository separates application code from deployment and infrastructure resources. Jenkins configuration is kept separately from application code, while `deploy/` and `infrastructure/` provide dedicated locations for deployment and infrastructure concerns.

## Project Status

The repository is structured as a broader trading platform rather than a single standalone script. Backend, frontend, workers, infrastructure, deployment, and documentation are maintained as separate areas so they can evolve independently.

## Security Notes

Do not commit API tokens, database passwords, JWT secrets, broker credentials, or other production configuration. Use environment-specific secret management for deployed environments.

## Disclaimer

Trading software can result in financial loss. This repository should be treated as engineering/software experimentation unless the trading logic, risk controls, and operational safeguards have been independently validated.
