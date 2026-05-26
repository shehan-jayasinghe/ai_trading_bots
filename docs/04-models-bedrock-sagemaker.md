# Models: Bedrock + SageMaker

## Purpose
Separate model responsibilities for clarity and control.

## Decision Model (Agent Reasoning)
- Provider: Bedrock (initial)
- Role: decide `call` / `put` / `skip` with confidence
- Inputs: indicators, risk state, recent context
- Outputs: structured decision JSON

## Embedding Model (RAG)
- Provider: SageMaker serverless endpoint (`deriv-ai-bot-dev-embed`) with HF `sentence-transformers/all-MiniLM-L6-v2`, OR Bedrock embeddings
- Role: encode trade summaries / market context for retrieval
- Outputs: vector + metadata

## Model Versioning
- Save model id/version per trade:
  - `decision_model_version`
  - `embedding_model_version`

## Guardrails
- JSON schema validation on model output
- Confidence threshold and risk veto path
