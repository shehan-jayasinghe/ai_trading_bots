# RAG + Tick Time-Series Data Strategy

## Purpose
Use both exact recent windows and semantic memory from historical outcomes.

## Data Classes
1. Market time-series (tick/OHLC windows)
2. Trade outcomes (win/loss, stake, profit, direction)
3. Indicator snapshots (at decision time)
4. Narrative summaries (for embeddings)

## Retrieval Design
- Exact retrieval: last N trades (5/10 windows) from DB
- Semantic retrieval: similar historical regimes from vector index
- Combine exact + semantic context for decision agent

## Tick 10 Focus (Phase 1)
- Single symbol pipeline for stability
- Consistent interval/window config
- Validate data completeness before decision

## Storage
- Structured facts: Postgres/Dynamo
- Vectors: pgvector/OpenSearch/S3 Vectors
- Raw large windows: S3 optional
