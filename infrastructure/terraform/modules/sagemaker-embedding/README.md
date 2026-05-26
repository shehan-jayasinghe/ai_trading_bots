# SageMaker embedding endpoint (serverless)

Deploys a **pay-per-invoke** serverless endpoint using the open-source Hugging Face model
`sentence-transformers/all-MiniLM-L6-v2` (384-dim embeddings).

## Invoke payload (workers)

```json
{"inputs": "workflow=... symbol=R_10 outcome=win ..."}
```

## Outputs

- `endpoint_name` — set `SAGEMAKER_EMBEDDING_ENDPOINT` for workers
- `invoke_policy_arn` — attach to EKS workers IRSA (`eks-irsa-sagemaker-embed`)

## First deploy note

Cold start can take several minutes while the container downloads the HF weights (VPC needs NAT).

## Disable

Set `enable_sagemaker_embedding = false` in `environments/dev/terraform.tfvars`.
