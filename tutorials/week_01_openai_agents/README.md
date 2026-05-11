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

Headless search uses **Playwright** (DuckDuckGo HTML first; if a bot challenge appears, it falls back to **Wikipedia** search results). Respect site terms and rate limits; this is for learning only.

Configure your API key (same as OpenAI Python defaults):

```bash
export OPENAI_API_KEY='your-key-here'
```

See `.env.example` for the variable name; you can copy values into a `.env` and load them with your own tooling if you prefer.

## Run

```bash
python main.py
```

## Requirements

- Python 3.11+
- A model ID your account supports (the script uses `gpt-4.1`; change it in `main.py` if needed).
