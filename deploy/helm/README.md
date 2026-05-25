# Helm charts

| Chart | Release | Namespace | Purpose |
|-------|---------|-----------|---------|
| [eks-cluster-addons](eks-cluster-addons/) | `eks-cluster-addons` | `kube-system` | ALB controller + external-dns |
| [eks-monitoring](eks-monitoring/) | `eks-monitoring` | `monitoring` | Loki + Promtail + Grafana |
| [deriv-postgres](deriv-postgres/) | `deriv-postgres` | `deriv-dev` | PostgreSQL (Bitnami) |
| [deriv-kafka](deriv-kafka/) | `deriv-kafka` | `deriv-dev` | Kafka (Bitnami) + topic job |
| [deriv-apps](deriv-apps/) | `deriv-apps` | `deriv-dev` | App workloads |
| [deriv-ingress](deriv-ingress/) | `deriv-ingress` | `deriv-dev` | ALB Ingress → `deriv-apps-*` Services |

## Deploy order

1. `terraform apply` (AWS + EBS CSI add-on)
2. `helm dependency update` on `deriv-postgres` and `deriv-kafka` (Jenkins does this automatically)
3. `jenkins/scripts/deploy/infrastructure/helm-eks-addons-deploy.sh`
4. `jenkins/scripts/deploy/helm-platform-deploy.sh` — postgres → kafka → apps → **ingress**
5. `jenkins/scripts/deploy/monitoring/helm-monitoring-deploy.sh`

Or one Jenkins job: **`deriv-deploy-platform`**.

Individual scripts: `deploy/data/`, `deploy/app/`, etc. — see `jenkins/scripts/README.md`.

## Migration from monolithic / apps-bound Ingress

```bash
# Legacy umbrella or Ingress still owned by deriv-apps release
helm uninstall deriv-platform -n deriv-dev 2>/dev/null || true
kubectl delete ingress deriv-apps -n deriv-dev --ignore-not-found
```

Then run `helm-platform-deploy.sh`.

## Chart dependencies

Subcharts are downloaded to `charts/*.tgz` on `helm dependency update` — **gitignored** (see `deploy/helm/.gitignore`).

## Service DNS

**Apps → data** (`deriv-apps/values.yaml`): `deriv-postgres-postgresql:5432`, `deriv-kafka:9092`.

**Ingress → apps** (`deriv-ingress/values.yaml`): `deriv-apps-backend`, `deriv-apps-frontend`.
