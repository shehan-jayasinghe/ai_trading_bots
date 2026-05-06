# Tracing and Observability

## Purpose
Track each run, LLM call, tool call, latency, errors, and decision lineage.

## Recommended Stack
- OpenTelemetry (service-level tracing)
- Optional Langfuse (LLM-level prompt/tool tracing)

## Trace Spans
- `run.start`
- `data.fetch_ticks`
- `indicators.compute`
- `rag.retrieve_exact`
- `rag.retrieve_semantic`
- `mm.compute_stake`
- `llm.decision`
- `broker.place_trade`
- `trade.persist`
- `rag.upsert`

## Required Trace Attributes
- `run_id`, `trade_id`, `symbol`
- `agent_name`, `tool_name`
- `model_id`, `latency_ms`
- `result` (win/loss/skip), `stake`, `profit`

## Alerts
- repeated decision parse failures
- elevated model latency
- broker execution errors
- abnormal daily loss
