# Jenkins scripts

## Layout

```text
scripts/
  deploy/
    helm-platform-deploy.sh       # main orchestrator (postgres → kafka → apps → ingress)
    preflight/                    # kubeconfig, EBS CSI, ECR checks
    infrastructure/               # ALB controller, external-dns
    data/                         # PostgreSQL, Kafka
    app/                          # backend, workers, frontend, ingress
    monitoring/                   # Loki, Promtail, Grafana
    diagnostics/                  # failure snapshots (post-build)
  lifecycle/
    park-platform.sh
    wake-platform.sh
    teardown-k8s-aws-orphans.sh
```

## Entry points

| Use case | Script |
|----------|--------|
| Full platform deploy | `deploy/helm-platform-deploy.sh` (Jenkins: `deriv-deploy-platform`) |
| Monitoring only | `deploy/monitoring/helm-monitoring-deploy.sh` (Grafana creds from `GRAFANA_SECRET_ID`) |
| Park / wake | `lifecycle/park-platform.sh`, `lifecycle/wake-platform.sh` |
| Pre-terraform destroy | `lifecycle/teardown-k8s-aws-orphans.sh` |

Jenkins job `deriv-deploy-platform` also runs preflight, infrastructure, and monitoring stages separately (see `deploy-platform.Jenkinsfile`).
