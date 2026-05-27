# Worker factory

Single-unit test runner for phase 0 (backend API + frontend UI).

## Run

```bash
cd worker_factory
cp .env.example .env   # optional
python run.py
```

Use one venv for the whole factory when you add dependencies:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt  # when added
.venv/bin/python run.py
```

## Layout

| Path | Role |
|------|------|
| `run.py` | Entrypoint |
| `config.py` | Paths + env |
| `agents/test_agent.py` | Test agent (backend → frontend) |
| `utils/` | Shared helpers |

## TODO

- `tests/api/` — 4 backend pytest tests
- `tests/playwright/` — 3 UI tests
- Incident capture / S3 (see `PLAN.md`)
