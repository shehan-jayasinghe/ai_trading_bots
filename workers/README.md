# Workers (Kafka + LangGraph)

Separate processes from FastAPI. See [docs/IMPLEMENTATION-GUIDE.md](../docs/IMPLEMENTATION-GUIDE.md).

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
cd workers
uv sync
cp .env.example .env
export PYTHONPATH=.

# Terminal 1 — planner
uv run python -m planner.main

# Terminal 2 — executor
uv run python -m executor.main
```

Manual execute test (skip planner):

```bash
cd workers
export PYTHONPATH=.
uv run python scripts/publish_execute_test.py
```

Dependencies live in `pyproject.toml` (`uv sync`). `requirements.txt` is kept for reference only.
