# Observability Helm values

Used by `jenkins/scripts/eks-monitoring.sh` (not a standalone chart).

| File | Purpose |
|------|---------|
| `loki-values-s3.yaml` | Loki SingleBinary + S3 (envsubst: bucket, region, IRSA role) |
| `loki-values-filesystem.yaml` | Fallback PVC when S3/IRSA not configured |
| `promtail-values.yaml` | Scrapes `deriv-dev`, `monitoring`, `kube-system` pods |
| `grafana-values.yaml` | Grafana + Loki datasource |

Install: see [docs/08-monitoring-logs.md](../../../docs/08-monitoring-logs.md).
