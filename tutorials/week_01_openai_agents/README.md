# Week 1 — OpenAI agents (planner + parallel research)

Minimal example: a planner breaks a task into steps, multiple research agents run concurrently with structured outputs, then a mock “email” sends the combined summary.

## Setup (isolated environment)

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

Headless search uses **Playwright** with DuckDuckGo HTML results. Respect site terms and rate limits; this is for learning only.

Configure your API key (same as OpenAI Python defaults):

```bash
export OPENAI_API_KEY='your-key-here'
```

See `.env.example` for the variable name; you can copy values into a `.env` and load them with your own tooling if you prefer.

## Run

```bash
python main.py
```

For a beginner-friendly single-file version:

```bash
python main_simple.py
```

## Code layout

- `main.py` keeps the original simple entrypoint.
- `main_simple.py` keeps the full tutorial in one readable file.
- `week_01_openai_agents/config.py` stores settings such as model name and search limits.
- `week_01_openai_agents/search.py` contains DuckDuckGo browser search.
- `week_01_openai_agents/agents/` contains the planner and researcher agents.
- `week_01_openai_agents/workflow.py` orchestrates the full planner → parallel research → email flow.

## Requirements

- Python 3.11+
- A model ID your account supports (the script uses `gpt-4.1`; change it in `week_01_openai_agents/config.py` if needed).
