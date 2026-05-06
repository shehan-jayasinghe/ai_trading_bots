# AI Agents and Tools

## Agent Roles
- Orchestrator Agent
- Data Agent (tick/time-series windows)
- Indicator/Strategy Agent (tool-calling)
- Decision Agent (LLM)
- Money Management Agent
- RAG Agent
- Guardrail Agent (optional)

## Tooling Pattern
- Indicators are tools (pure functions)
- Strategy evaluators are tools
- Broker execution is a controlled service (not direct free-form tool)

## Initial Scope
- Deriv Tick 10 only
- Fixed strategy set from migrated code
- Strict output contracts (Pydantic/JSON schema)

## Safety
- Block trade if:
  - risk limits exceeded
  - malformed decision output
  - missing required market window
