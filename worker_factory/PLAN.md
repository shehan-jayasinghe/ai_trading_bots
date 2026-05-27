# Worker factory — phased plan

## Current step — Phase 0: Auth testing (API + UI)

**Status: in progress.** Implement and run tests until signup/login API and UI responses pass. No Lambda/SQS/Jenkins automation yet.

| Deliverable | Location |
|-------------|----------|
| **Test agent** | [agents/test_runner/run.py](agents/test_runner/run.py) — `python -m agents.test_runner.run` (or container `ENTRYPOINT`) |
| Scenario catalog | [tests_catalog/scenarios.yaml](tests_catalog/scenarios.yaml) |
| API tests (4) | [tests/api/test_auth_api.py](tests/api/test_auth_api.py) |
| UI tests (3) | [tests/playwright/auth.spec.ts](tests/playwright/auth.spec.ts) |
| Failure capture (S3 + local) | [tests/helpers/incident.py](tests/helpers/incident.py) |
| Pull tool | [tests/helpers/pull_incident.py](tests/helpers/pull_incident.py) |
| Runbook | [docs/TEST-FLOWS.md](docs/TEST-FLOWS.md) |

**Run:** `cd worker_factory && python3 -m agents.test_runner.run` (backend first, then frontend; stops on fail). On fail → `.factory-incidents/` and optionally `s3://LOKI_S3_BUCKET/factory/errors/<backend|frontend>/...`.

**Exit criteria for Phase 0:** all scenarios in TEST-FLOWS run order pass against dev or local `APP_DOMAIN` / `API_DOMAIN`.

---

## Goal (full factory)

Test the platform (UI login/signup, API, deploy smoke) → on failure upload evidence to S3 → classify error → Bedrock triage → optional fix PR or vector + user comms. **Separate** from trading `workers/executor/`.

## Flow (later phases)

```text
[Test runner] scenarios (auth.login.ui, auth.signup.api, …)
  → fail → [Error capture] → S3 errors/<date>/<incident_id>/
  → [Classifier] code | information | unknown
       ├── code        → [Fix agent] → GitHub PR (Bedrock / human + Cursor on branch)
       └── information → [Vector writer] + optional [User comms] (admin-approved email)
  → [Midnight reviewer] batch: scan new errors/, dedupe via factory vector index
```

## Folder structure

Layout under `worker_factory/`. **Phase 0** paths exist; other agents/infra are later.

```text
worker_factory/
├── README.md
├── PLAN.md
├── prompts.md
├── docs/
│   └── TEST-FLOWS.md          # phase 0 run order + env
├── tests_catalog/
│   └── scenarios.yaml
├── config/
│   └── settings.py            # FACTORY_ROOT paths + .env (all agents import this)
├── .env.example
├── agents/
│   └── test_runner/           # phase 0: run.py (pytest + Playwright)
├── tests/
│   ├── README.md
│   ├── requirements.txt
│   ├── conftest.py
│   ├── api/test_auth_api.py
│   ├── playwright/            # package.json + auth.spec.ts
│   └── helpers/               # incident, pull, record_ui_failure
├── knowledge/                 # (planned)
├── schemas/                   # (planned)
├── agents/                    # (planned) one subfolder per logical agent
│   ├── test_runner/
│   ├── error_capture/
│   ├── classifier/
│   ├── vector_writer/
│   ├── user_comms/
│   ├── fix_agent/
│   └── midnight_reviewer/
│
├── tools/                     # (planned) shared: s3, bedrock, github, vector, redact
└── infra/                     # (planned) factory bucket, IAM, EventBridge (or link to terraform)
```

### Agents → folders

| Agent | Folder | Responsibility |
|--------|--------|----------------|
| Test runner | `tests/`, `tests_catalog/` | Run login/signup and platform scenarios; tester/admin severity metadata |
| Error capture | `agents/error_capture/`, `tools/` | Build FailureBundle; write **errors/** (not normal **logs/**) |
| Classifier | `agents/classifier/` | `code` → fix path; `information` → vector/comms; never auto-fix wrong-password as code |
| Vector writer | `agents/vector_writer/` | Upsert **factory-incidents** index (not trade `trade-embeddings`) |
| User comms | `agents/user_comms/` | Email drafts from redacted context; v1 = admin approve, not auto-send |
| Fix agent | `agents/fix_agent/` | Clone latest GitHub, Bedrock diff, re-test, PR |
| Midnight reviewer | `agents/midnight_reviewer/` | Scheduled scan of `errors/`, dedupe, re-triage |

### S3 layout (reuse `LOKI_S3_BUCKET` — single source of truth)

Loki chunk keys stay untouched. Factory writes under `factory/errors/` by **component**:

```text
s3://<LOKI_S3_BUCKET>/
├── (Loki-managed keys)
└── factory/
    └── errors/
        ├── backend/<yyyy>/<mm>/<dd>/<incident_id>/   # API tests
        ├── frontend/<yyyy>/<mm>/<dd>/<incident_id>/ # Playwright
        └── workers/<yyyy>/<mm>/<dd>/<incident_id>/   # later
            ├── bundle.json
            ├── api_response.json   # backend only
            └── ui_console.log      # frontend only
```

### Repo areas the factory tests (unchanged location)

| Path | Factory concern |
|------|-----------------|
| `frontend/src/app/login/`, `signup/`, `api/auth/` | UI + signup tests, form/NextAuth errors |
| `backend/app/routes/`, `core/exceptions.py` | API status + `detail` in bundle |
| `workers/` | Trading runtime — **not** factory agents; optional smoke scenarios only |
| `deploy/`, `jenkins/` | Helm/terraform smoke scenarios |

## What can be added because of worker factory

New capabilities (do not mix into `workers/executor/`):

- **Auth regression tests** (Playwright + API) with structured failure artifacts.
- **Error vs log separation** in S3 for midnight batch and triage.
- **Classification gate** so only **code** errors open PRs; **information** errors go to vector DB + optional user email.
- **Factory vector index** for similar incidents and fix history (separate from trade RAG).
- **Admin/tester metadata** on scenarios (severity, error level) for triage hints.
- **Midnight job** to re-process `errors/` like a repeat test flow.
- **Allowlisted auto-fix** paths: `frontend/`, `backend/`, `tests/`, `worker_factory/`, `deploy/` — not secrets or `.env`.

## Phase 1 — Safety (after Phase 0 green)

- Factory IAM: read S3 history, Bedrock invoke, GitHub PR scope — no trade execution or infra destroy.
- All changes via PR; allowlisted paths only (`tests/`, `workers/`, `deploy/`, `worker_factory/`, `docs/`, `frontend/`, `backend/`).
- Redact secrets in CI artifacts (passwords, tokens, `AUTH_SECRET`).

## Phase 2 — Failure capture

S3 prefix `errors/<date>/<incident_id>/`: `bundle.json`, `api_response.json`, optional `ui_console.log`, `junit.xml`. Fields: `scenario_id`, `severity`, `commit_sha`, `ci_run_url`, `error_summary`, optional redacted `user_hint`.

## Phase 3 — Triage + classify (Lambda)

Load bundle + `knowledge/` → Bedrock → GitHub issue/comment + `error_class`. No git clone in Lambda.

## Phase 4 — Fix + PR (CodeBuild/ECS)

Only when `error_class=code`. Clone at `commit_sha`, Bedrock diff (`prompts.md`), re-run scenario, push `factory/fix-<id>`, open PR. Cursor/Antigravity = optional human step on same branch.

## Phase 5 — Incident memory + midnight

- Factory S3 Vectors index (e.g. `factory-incidents`) for information incidents and resolved fixes.
- EventBridge schedule → midnight reviewer lists new `errors/`, dedupes, routes to classifier/fix/comms.

---

## AWS overview (how pieces connect)

Keep **trade** RAG (`trade-embeddings`, workers IRSA on EKS) **separate** from factory IAM and buckets.

```mermaid
flowchart TB
  subgraph dev["Repo / CI"]
    JEN[Jenkins or GitHub Actions]
    PW[Playwright / API tests]
    APP[EKS: frontend + backend + workers]
  end

  subgraph aws_storage["AWS storage"]
    S3L[(S3 factory-history bucket)]
    S3L --> logs_prefix[logs/]
    S3L --> errs_prefix[errors/]
    VDB[(S3 Vectors: factory-incidents)]
  end

  subgraph aws_compute["AWS compute"]
    EB[EventBridge rules]
    L1[Lambda: classifier triage]
    CB[CodeBuild or ECS: fix + PR job]
    EB2[EventBridge cron: midnight]
    L2[Lambda or ECS: midnight reviewer]
  end

  subgraph aws_ai["AWS AI"]
    BR[Bedrock invoke]
    SM[SageMaker embed optional]
  end

  subgraph external["External"]
    GH[GitHub repo + App token]
    SES[SES optional user email]
  end

  JEN --> PW
  PW --> APP
  PW -->|fail upload bundle| errs_prefix
  APP -->|normal logs| logs_prefix
  APP -->|5xx beacon optional| errs_prefix

  errs_prefix -->|ObjectCreated| EB
  EB --> L1
  L1 --> BR
  L1 --> GH
  L1 -->|information| VDB
  L1 -->|code start job| CB
  CB --> BR
  CB --> GH

  EB2 --> L2
  L2 --> errs_prefix
  L2 --> VDB
  L2 --> BR

  SM --> VDB
```

### AWS setup checklist

| Step | AWS resource | Purpose |
|------|----------------|--------|
| 1 | **S3 bucket** e.g. `deriv-ai-bot-factory-history` (new; not trade vectors bucket) | `logs/` + `errors/` |
| 2 | **S3 Vectors** bucket + index `factory-incidents` (384-dim, cosine) | Similar incidents / midnight dedupe; can reuse SageMaker embed endpoint |
| 3 | **IAM role** e.g. `deriv-factory-worker` | S3 factory bucket; `s3vectors:QueryVectors` / `PutVectors` on factory index; `bedrock:InvokeModel`; **no** trade execution / EKS admin |
| 4 | **Lambda** + **EventBridge** on `s3:ObjectCreated` under `errors/` | Classifier triage (Phase 3) |
| 5 | **CodeBuild** or **ECS** + optional **Step Functions** | Fix agent: clone, patch, re-test, PR (Phase 4) |
| 6 | **Secrets Manager** | GitHub App key; optional SES |
| 7 | **EventBridge schedule** e.g. `cron(0 0 * * ? *)` UTC | Midnight reviewer (Phase 5) |
| 8 | **Bedrock** model enabled in region (e.g. `us-west-1`) | Triage + fix prompts |
| 9 | **CI/Jenkins** IAM or OIDC | Upload to `errors/` on test failure |

### What runs where (today vs later)

| Piece | In repo today | In AWS when built |
|--------|----------------|-------------------|
| Auth UI/API | `frontend` login/signup, `backend` routes | Tested by CI |
| Factory plan | `worker_factory/PLAN.md` | — |
| Classifier / fix / midnight | Not implemented | Lambda, CodeBuild, EventBridge |
| Trading bot | `workers/` on EKS | Unchanged |

### One-page mental model

```text
                    ┌─────────────────────────────────────┐
                    │           AWS (factory)              │
                    │  S3 logs/ + errors/  │  S3 Vectors   │
                    │  Bedrock  │  Lambda  │  CodeBuild   │
                    └───────────┬─────────────────────────┘
                                │
     Flow A (tests) ────────────┼── CI fail → errors/ → classify → PR or vector
     Flow B (live)  ────────────┼── app error → errors/ → same classifier
     Flow C (night) ───────────┴── cron → scan errors/ → dedupe → classify again
```

---

## Three main flows

### Flow A — Testing (login/signup + smoke)

Primary path to build first.

```mermaid
sequenceDiagram
  participant T as Test runner CI
  participant UI as Frontend login/signup
  participant API as Backend FastAPI
  participant S3 as S3 errors/
  participant C as Classifier Lambda
  participant B as Bedrock
  participant F as Fix CodeBuild
  participant V as factory-incidents
  participant GH as GitHub

  T->>UI: Playwright login/signup
  T->>API: signup API smoke
  alt pass
    T-->>T: green
  else fail
    T->>S3: bundle.json + logs + screenshot
    S3->>C: EventBridge trigger
    C->>B: triage + classify
    B-->>C: code or information
    alt code
      C->>F: start fix job
      F->>GH: branch + PR
    else information
      C->>V: embed incident metadata
      Note over C: optional user comms draft to admin
    end
  end
```

- **When:** every CI run or manual “run auth suite.”
- **Chain:** Test runner → Error capture → Classifier → Fix **or** Vector (+ comms later).

### Flow B — Live app / runtime error

Same pipeline when a real user hits an error (optional v2).

```mermaid
flowchart LR
  U[User browser] --> FE[Next.js]
  FE -->|API error| BE[FastAPI AppError or 500]
  BE --> LOGS[S3 logs/]
  FE -->|error boundary optional| CAP[Admin beacon or log shipper]
  CAP --> ERR[S3 errors/]
  ERR --> C[Classifier]
  C --> B{code or information?}
  B -->|wrong password| V[Vector + email draft]
  B -->|500 bug| PR[Fix PR]
```

- **When:** staging/production incident, not only CI.
- **Rules:** redact password/tokens; store hashed `user_id` or email domain only in vector metadata.

### Flow C — Midnight batch

Re-process incidents that landed in `errors/` (missed events, dedupe, retry `unknown`).

```mermaid
flowchart TB
  CRON[EventBridge midnight] --> M[Midnight reviewer]
  M --> LIST[List S3 errors/ since watermark]
  M --> Q[Query factory-incidents similar?]
  Q -->|duplicate| SKIP[Link or skip]
  Q -->|new or unprocessed| M2[Classifier again]
  M2 --> CODE[code: queue fix if no PR yet]
  M2 --> INFO[information: vector + comms queue]
```

- **When:** once per night (or every 6h).
- **Why:** catch missed EventBridge deliveries; dedupe repeated login errors; retry classification.

---

## Prompts

See [prompts.md](prompts.md).
