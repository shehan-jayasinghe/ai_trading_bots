# Week 2 - LangChain agents

Minimal example: the same planner -> parallel research -> mock email flow from Week 1, rewritten with LangChain chains.

Week 1 shows the raw OpenAI SDK calls. Week 2 shows the same shape using `ChatOpenAI`, `ChatPromptTemplate`, and `with_structured_output`.

## Setup

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

Headless search uses Playwright with DuckDuckGo HTML results. Respect site terms and rate limits; this is for learning only.

Configure your API key:

```bash
export OPENAI_API_KEY='your-key-here'
```

See `.env.example` for the variable name.

## Run

```bash
python main.py
```

For a beginner-friendly single-file version:

```bash
python main_simple.py
```

You can also run the package:

```bash
python -m week_02_langchain_agents
```

## Code layout

- `main.py` keeps the simple tutorial entrypoint.
- `main_simple.py` keeps the full LangChain tutorial in one readable file.
- `week_02_langchain_agents/config.py` stores settings such as model name and search limits.
- `week_02_langchain_agents/search.py` contains DuckDuckGo browser search.
- `week_02_langchain_agents/chains.py` contains the LangChain planner and researcher chains.
- `week_02_langchain_agents/workflow.py` orchestrates planner -> parallel research -> email.

## Requirements

- Python 3.11+
- A model ID your account supports. The script uses `gpt-4.1`; change it in `week_02_langchain_agents/config.py` if needed.
