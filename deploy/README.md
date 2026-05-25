# Deploy — Helm platform (dev)

**Plan A:** four platform charts — `deriv-postgres`, `deriv-kafka`, `deriv-apps`, `deriv-ingress` (ALB routes to app Services).

Requires Terraform **`enable_eks = true`** in `infrastructure/terraform/environments/dev/terraform.tfvars`.

| Layer | Tool |
|-------|------|
| Cluster + ECR + **EBS CSI** | Terraform `infrastructure/terraform/environments/dev` |
| Platform on EKS | Jenkins `deriv-deploy-platform` or `jenkins/scripts/deploy/` |
| Images | Dockerfiles in `deploy/docker/` → push to ECR |

**Storage:** Helm `values-dev.yaml` sets `storageClass: gp2`. EKS provisions volumes via the **aws-ebs-csi-driver** add-on (Terraform). Without it, Postgres/Kafka PVCs stay `Pending`.

**Bitnami images:** Chart defaults pointed at removed `docker.io/bitnami/*` tags. `values.yaml` uses `docker.io/bitnamilegacy/*` for Postgres/Kafka (legacy archive matching pinned subchart versions).

Prod is stubbed (`values-prod.yaml`) — dev only for now.

---

## 1 — Build and push images

```bash
cd /path/to/deriv_ai_bot

# Registry from terraform
cd infrastructure/terraform/environments/dev
export REGISTRY=$(terraform output -json ecr_repository_urls | python3 -c "import sys,json; u=json.load(sys.stdin)['deriv-backend']; print(u.split('/')[0])")
export AWS_PROFILE=default
aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin "$REGISTRY"

docker build -f deploy/docker/backend.Dockerfile -t "$REGISTRY/deriv-backend:latest" .
docker build -f deploy/docker/workers.Dockerfile -t "$REGISTRY/deriv-workers:latest" .
docker build -f deploy/docker/frontend.Dockerfile \
  --build-arg NEXT_PUBLIC_BOT_BASE_URL=https://api.testenvlab.shop \
  -t "$REGISTRY/deriv-frontend:latest" .
docker push "$REGISTRY/deriv-backend:latest"
docker push "$REGISTRY/deriv-workers:latest"
docker push "$REGISTRY/deriv-frontend:latest"
```

Set `ECR_REGISTRY` in Jenkins global environment variables to `$REGISTRY` (see `jenkins/global-env.example`).

---

## 2 — Secrets (AWS Secrets Manager)

**Not in Git.** Terraform creates the secret shell; you store values once:

```bash
cd infrastructure/terraform/environments/dev
terraform output -raw platform_secret_populate_command
# Replace CHANGE_ME, then run the printed aws secretsmanager put-secret-value command
```

JSON keys: `POSTGRES_PASSWORD`, `AUTH_SECRET`, `OPENAI_API_KEY` (optional).

Grafana secret (`terraform output grafana_secret_populate_command`): `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`.

**Jenkins deploy** reads `PLATFORM_SECRET_ID` → K8s `deriv-platform-app-secrets`; `GRAFANA_SECRET_ID` → `grafana-admin` in `monitoring`.

**Infra config** (not secrets): Jenkins global environment variables only — see `jenkins/global-env.example` for the full list (ECR, EKS, ACM ARNs, domains).

After `terraform apply`, set Jenkins globals from `terraform output`:

| Jenkins env | Terraform output |
|-------------|------------------|
| `ECR_REGISTRY` | `ecr_registry` |
| `PLATFORM_SECRET_ID` | `platform_secret_name` |
| `VPC_ID` | `vpc_id` |
| `ALB_CONTROLLER_ROLE_ARN` | `aws_lb_controller_role_arn` |
| `EXTERNAL_DNS_ROLE_ARN` | `external_dns_role_arn` |
| `LOKI_S3_BUCKET` / `LOKI_ROLE_ARN` | `loki_s3_bucket` / `loki_role_arn` |
| `GRAFANA_SECRET_ID` | `grafana_secret_name` |
| `GRAFANA_ACM_CERTIFICATE_ARN` | `grafana_acm_certificate_arn` |
| `GRAFANA_DOMAIN` | `grafana.testenvlab.shop` |

EBS CSI is installed by Terraform. Verify with `aws eks describe-addon` (see §3 below).

Public URLs (after Ansible deploy + DNS propagation): `app_url` → `https://app.testenvlab.shop`, `api_url` → `https://api.testenvlab.shop`.

---

## 3 — EBS CSI (once per cluster)

After `terraform apply`, confirm the add-on (also checked by Ansible / Jenkins deploy):

```bash
aws eks describe-addon --cluster-name deriv-ai-bot-dev --addon-name aws-ebs-csi-driver --region us-west-1 --query addon.status
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-ebs-csi-driver
```

Expect add-on status `ACTIVE` and `ebs-csi-controller-*` **Running**.

---

## 4 — Helm dependencies (once)

```bash
helm dependency update deploy/helm/deriv-postgres
helm dependency update deploy/helm/deriv-kafka
```

---

## 5 — Deploy (Jenkins or scripts)

```bash
# From repo root — same order as deriv-deploy-platform
export AWS_REGION=us-west-1 EKS_CLUSTER_NAME=deriv-ai-bot-dev
# ... set VPC_ID, IRSA ARNs, ECR_REGISTRY, etc. (see jenkins/global-env.example)

jenkins/scripts/deploy/preflight/platform-preflight.sh
jenkins/scripts/deploy/infrastructure/helm-eks-addons-deploy.sh
jenkins/scripts/deploy/helm-platform-deploy.sh
jenkins/scripts/deploy/monitoring/helm-monitoring-deploy.sh
```

See `jenkins/README.md` and `deploy/helm/README.md`.

---

## 6 — Verify

```bash
aws eks update-kubeconfig --region us-west-1 --name deriv-ai-bot-dev
kubectl get pvc -n deriv-dev
kubectl get pods -n deriv-dev
kubectl get ingress -n deriv-dev
kubectl logs -n deriv-dev -l app.kubernetes.io/component=backend --tail=50
curl -sS https://api.testenvlab.shop/hello
curl -sS -o /dev/null -w "%{http_code}\n" https://app.testenvlab.shop/
```

---

## CI (build images)

Jenkins pipelines: `jenkins/README.md` — `deriv-build-backend`, `deriv-build-workers` push to ECR.

---

## Layout

```text
deploy/
  docker/
  helm/
    eks-cluster-addons/   # ALB controller + external-dns
    eks-monitoring/       # Loki + Promtail + Grafana
    deriv-postgres/       # PostgreSQL
    deriv-kafka/          # Kafka + topic bootstrap job
    deriv-apps/           # backend, workers, frontend
    deriv-ingress/        # ALB Ingress (app + API hosts)
```

---

## Env handling

| Type | Where |
|------|--------|
| Defaults | `values.yaml` |
| Dev overrides | `values-dev.yaml` |
| Secrets | AWS Secrets Manager → K8s `deriv-platform-app-secrets` (`deploy/helm-platform-deploy.sh`) |
| CI image tag | Jenkins `IMAGE_TAG` → `--set image.tag=...` |
