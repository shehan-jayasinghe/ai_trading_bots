FROM python:3.12-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY workers/pyproject.toml workers/uv.lock ./
RUN uv sync --frozen --no-dev

COPY workers/ ./

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
