# Agentic Worker Factory

Specs for **test → failure capture → triage → PR** automation. Not part of live trading (`workers/executor/`).

| File | Purpose |
|------|---------|
| [PLAN.md](PLAN.md) | Phased rollout, folder structure, **AWS setup**, **3 flows** (test / live / midnight) |
| [prompts.md](prompts.md) | Bedrock prompt drafts (triage, fix, PR summary) |

No runtime code here yet. Trade RAG stays in `workers/` (separate S3 index if factory memory is added later).
