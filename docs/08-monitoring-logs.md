# Platform logs in Grafana (Loki + Promtail)

## Stack

| Component | Role |
|-----------|------|
| **Promtail** | DaemonSet — reads container stdout from `deriv-dev` pods |
| **Loki** | Log store (S3 in AWS dev; PVC fallback if bucket unset) |
| **Grafana** | UI — Explore logs with LogQL |

Flow: `backend` / `planner` / `executor` → stdout → Promtail → Loki → Grafana.

Apps use Python `logging` to stdout — no code changes required.

## Terraform (once per env)

```bash
cd infrastructure/terraform/environments/dev
terraform apply
terraform output -raw loki_s3_bucket
terraform output -raw loki_role_arn
```

Add to Jenkins globals or `jenkins/config/dev.env`:

```bash
LOKI_S3_BUCKET=<terraform output>
LOKI_ROLE_ARN=<terraform output>
```

S3 lifecycle defaults to **90 days** (`loki_s3_lifecycle_expire_days`) for the next AI/log-analysis phase.

## Deploy

**With platform (default):** `deriv-deploy-platform` runs `jenkins/scripts/eks-monitoring.sh` after Helm.

**Standalone:** job `deriv-deploy-monitoring` → `jenkins/pipelines/deploy-monitoring.Jenkinsfile`.

Skip on deploy: `MONITORING_ENABLED=false`.

## Access Grafana

```bash
aws eks update-kubeconfig --region us-west-1 --name deriv-ai-bot-dev
kubectl port-forward -n monitoring svc/grafana 3000:80
```

Open http://localhost:3000 — user `admin`, password:

```bash
kubectl get secret grafana-admin -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d && echo
```

## LogQL examples

```logql
{namespace="deriv-dev", component="backend"}
{namespace="deriv-dev", component="planner"}
{namespace="deriv-dev", component="executor"}
{namespace="deriv-dev"} |= "ERROR"
```

## Files

- `deploy/helm/observability/` — Helm values for Loki / Promtail / Grafana
- `jenkins/scripts/eks-monitoring.sh` — install script
- `infrastructure/terraform/modules/loki-s3` — S3 bucket
- `infrastructure/terraform/modules/eks-irsa-loki` — IRSA for `monitoring:loki`
