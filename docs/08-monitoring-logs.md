# Platform logs in Grafana (Loki + Promtail)

## Stack

| Component | Role |
|-----------|------|
| **Promtail** | DaemonSet — reads container stdout from `deriv-dev` pods |
| **Loki** | Log store (S3 chunks in AWS dev; small local PVC for compactor/WAL; full PVC if bucket unset) |
| **Grafana** | UI — Explore logs with LogQL |

Flow: `backend` / `planner` / `executor` → stdout → Promtail → Loki → Grafana.

Apps use Python `logging` to stdout — no code changes required.

## Terraform (once per env)

```bash
cd infrastructure/terraform/environments/dev
terraform apply
terraform output -raw loki_s3_bucket
terraform output -raw loki_role_arn
terraform output -raw grafana_acm_certificate_arn
terraform output -raw grafana_secret_populate_command
```

**Grafana admin credentials** (AWS Secrets Manager, not in Git):

```bash
# Run the populate command from terraform output; set a strong password:
# {"GRAFANA_ADMIN_USER":"admin","GRAFANA_ADMIN_PASSWORD":"YOUR_PASSWORD"}
```

Add to Jenkins global environment variables (see `jenkins/global-env.example`):

```bash
LOKI_S3_BUCKET=<terraform output>
LOKI_ROLE_ARN=<terraform output>
GRAFANA_SECRET_ID=deriv-ai-bot/dev/grafana
GRAFANA_DOMAIN=grafana.testenvlab.shop
GRAFANA_ACM_CERTIFICATE_ARN=<terraform output grafana_acm_certificate_arn>
```

## Deploy

**With platform (default):** `deriv-deploy-platform` runs `deploy/monitoring/helm-monitoring-deploy.sh`.

Skip on platform job: `DEPLOY_MONITORING=false`.

Deploy syncs Secrets Manager → K8s secret `grafana-admin` (`admin-user` / `admin-password` keys for the Grafana chart).

## Access Grafana (public URL)

After deploy and DNS propagation:

**https://grafana.testenvlab.shop** (or your `GRAFANA_DOMAIN`)

Login with credentials from Secrets Manager:

```bash
aws secretsmanager get-secret-value \
  --region us-west-1 \
  --secret-id deriv-ai-bot/dev/grafana \
  --query SecretString --output text | jq .
```

Or read the synced K8s secret:

```bash
kubectl get secret grafana-admin -n monitoring -o jsonpath='{.data.admin-user}' | base64 -d && echo
kubectl get secret grafana-admin -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d && echo
```

**Fallback (no ACM / local debug):**

```bash
kubectl port-forward -n monitoring svc/grafana 3000:80
# http://localhost:3000
```

## LogQL examples

```logql
{namespace="deriv-dev", component="backend"}
{namespace="deriv-dev", component="planner"}
{namespace="deriv-dev", component="executor"}
{namespace="deriv-dev"} |= "ERROR"
```

## Troubleshooting

**Loki `CrashLoopBackOff`: `mkdir /var/loki: read-only file system`** — S3 mode still needs `singleBinary.persistence` (see `values-dev-s3.yaml`). Redeploy monitoring after fixing values.

**Promtail `0/1`, readiness HTTP 500** — usually follows unhealthy Loki; fix Loki first.

## Files

- `deploy/helm/eks-monitoring/` — umbrella chart (Loki / Promtail / Grafana dependencies)
- `jenkins/scripts/deploy/monitoring/helm-monitoring-deploy.sh` — Secrets sync + Helm upgrade
- `infrastructure/terraform/environments/dev/secrets.tf` — `grafana` Secrets Manager secret
- `infrastructure/terraform/modules/loki-s3` — S3 bucket
- `infrastructure/terraform/modules/eks-irsa-loki` — IRSA for `monitoring:loki`
