# Worker factory — phased plan

Documentation only. No Lambda, ECS, or CI code in this folder yet.

## Goal

Test the platform → on failure upload evidence to S3 → Bedrock triage → (later) CodeBuild/ECS applies patch and opens a GitHub PR. Separate from trading `workers/executor/`.

## Flow

```text
CI tests (scenario ids — define in CI when implemented)
  → fail → FailureBundle in S3
  → EventBridge → Lambda triage (Bedrock, see prompts.md)
  → optional CodeBuild: clone, patch, re-test, PR (prompts.md)
  → human merge
```

## Phase 1 — Safety

- Factory IAM: read S3 history, Bedrock invoke, GitHub PR scope — no trade execution or infra destroy.
- All changes via PR; allowlisted paths only (`tests/`, `workers/`, `deploy/`, `worker_factory/`, `docs/`).
- Redact secrets in CI artifacts.

## Phase 2 — Failure capture

S3 prefix `failures/<date>/<incident_id>/`: `bundle.json`, `stderr.log`, `junit.xml`. Fields: `scenario_id`, `severity`, `commit_sha`, `ci_run_url`, `error_summary`.

## Phase 3 — Triage (Lambda)

Load bundle + platform KB (component runbooks) → Bedrock → GitHub issue/comment. No git clone in Lambda.

## Phase 4 — Fix + PR (CodeBuild/ECS)

Clone at `commit_sha`, Bedrock diff, run failing scenario, push `factory/fix-<id>`, open PR.

## Phase 5 — Incident memory (optional)

Separate S3 Vectors index (e.g. `factory-incidents`) for past fixes—not the trade index.

## Prompts

See [prompts.md](prompts.md).
