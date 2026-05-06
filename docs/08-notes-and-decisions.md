# Notes and Decisions Log

## Current Decisions
- FastAPI as HTTP layer
- EventBridge + Lambda scheduler
- Job-based execution: `POST /runs` returns quickly, worker does trade loop in background
- Bedrock for decision model
- SageMaker/Bedrock for embeddings
- RAG enabled with exact + semantic retrieval
- Initial market: Deriv Tick 10 index only

## Open Questions
- Final vector backend (pgvector vs OpenSearch vs S3 Vectors)
- Final tracing stack (OTel only vs OTel + Langfuse)
- Exact MM formula version from spreadsheet
- Queue/worker implementation choice (SQS + Fargate worker vs Step Functions)

## Next Milestones
1. Migrate indicator/strategy tools
2. Implement run + trade persistence with queued background jobs
3. Add scheduler path (EventBridge -> Lambda -> enqueue run)
4. Add decision model + schema guardrails
5. Add tracing and dashboards
