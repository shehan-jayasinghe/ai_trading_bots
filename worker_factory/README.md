# Agentic Worker Factory

Specs for **test → failure capture → triage → PR** automation. Not part of live trading (`workers/executor/`).

| File | Purpose |
|------|---------|
| [PLAN.md](PLAN.md) | Phased rollout (safety → S3 → Lambda → CodeBuild → optional memory) |
| [prompts.md](prompts.md) | Bedrock prompt drafts (triage, fix, PR summary) |

No runtime code here yet. Trade RAG stays in `workers/` (separate S3 index if factory memory is added later).
