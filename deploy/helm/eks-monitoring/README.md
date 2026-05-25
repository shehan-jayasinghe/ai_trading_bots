# eks-monitoring Helm chart

Umbrella chart: **Loki** + **Promtail** + **Grafana** (chart dependencies).

```bash
helm dependency update deploy/helm/eks-monitoring
helm upgrade --install eks-monitoring deploy/helm/eks-monitoring \
  -n monitoring --create-namespace \
  -f values.yaml -f values-dev.yaml \
  [-f values-dev-s3.yaml --set loki.loki.storage.bucketNames.chunks=BUCKET ...]
```

Jenkins: `deriv-deploy-platform` (`DEPLOY_MONITORING=true`) or `jenkins/scripts/deploy/monitoring/helm-monitoring-deploy.sh`.

Grafana admin credentials: AWS Secrets Manager `deriv-ai-bot/dev/grafana` → K8s `grafana-admin`. Public URL: `https://grafana.testenvlab.shop` (ACM + ALB Ingress).

See [docs/08-monitoring-logs.md](../../../docs/08-monitoring-logs.md).
