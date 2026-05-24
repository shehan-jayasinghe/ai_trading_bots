# Deploy — Helm platform (dev)

**Plan A:** umbrella chart `helm/deriv-platform` (Postgres + Kafka + backend + workers + frontend + ALB ingress).

| Layer | Tool |
|-------|------|
| Cluster + ECR + **EBS CSI** | Terraform `infrastructure/terraform/environments/dev` |
| Platform on EKS | Ansible `playbooks/eks-platform.yml` |
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

Set `image_registry` in `infrastructure/ansible/inventories/dev/group_vars/eks.yml` to `$REGISTRY`.

---

## 2 — Secrets (AWS Secrets Manager)

**Not in Git.** Terraform creates the secret shell; you store values once:

```bash
cd infrastructure/terraform/environments/dev
terraform output -raw platform_secret_populate_command
# Replace CHANGE_ME, then run the printed aws secretsmanager put-secret-value command
```

JSON keys: `POSTGRES_PASSWORD`, `AUTH_SECRET`, `OPENAI_API_KEY` (optional).

**Jenkins deploy** reads `PLATFORM_SECRET_ID` (default `deriv-ai-bot/dev/platform`) and syncs to K8s `deriv-platform-app-secrets`.

**Infra config** (not secrets): `jenkins/config/dev.env.example` or Jenkins globals — ECR, EKS, ACM ARNs, domains.

After `terraform apply`, copy into `eks.yml` (or use `terraform output -raw`):

| `eks.yml` key | Terraform output |
|---------------|------------------|
| `image_registry` | `ecr_registry` |
| `platform_secret_id` | `platform_secret_name` |
| `vpc_id` | `vpc_id` |
| `alb_controller_role_arn` | `aws_lb_controller_role_arn` |
| `external_dns_role_arn` | `external_dns_role_arn` |
| `app_acm_certificate_arn` | `app_acm_certificate_arn` |
| `api_acm_certificate_arn` | `api_acm_certificate_arn` |

EBS CSI is installed by Terraform (no `eks.yml` key). Verify with `aws eks describe-addon` (see §3 below).

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
helm dependency update deploy/helm/deriv-platform
```

---

## 5 — Deploy with Ansible

```bash
cd infrastructure/ansible
ansible-galaxy collection install -r requirements.yml

export AWS_PROFILE=default
ansible-playbook playbooks/eks-platform.yml -vv
```

Or Helm only (after secret exists):

```bash
kubectl create namespace deriv-dev --dry-run=client -o yaml | kubectl apply -f -
# create secret manually or via Ansible first

helm upgrade --install deriv-platform deploy/helm/deriv-platform \
  -n deriv-dev --create-namespace \
  -f deploy/helm/deriv-platform/values.yaml \
  -f deploy/helm/deriv-platform/values-dev.yaml \
  --set image.registry="$REGISTRY" \
  --set image.tag=latest \
  --wait --timeout 20m
```

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
  docker/           # backend, workers, frontend Dockerfiles
  helm/deriv-platform/
    Chart.yaml      # Bitnami postgresql + kafka dependencies
    values.yaml
    values-dev.yaml
    values-prod.yaml   # stub
    templates/         # backend, workers, frontend, ingress, kafka topics job
```

---

## Env handling

| Type | Where |
|------|--------|
| Defaults | `values.yaml` |
| Dev overrides | `values-dev.yaml` |
| Secrets | AWS Secrets Manager → K8s `deriv-platform-app-secrets` (Jenkins deploy or Ansible) |
| CI image tag | `--set image.tag=$GIT_SHA` or `eks.yml` `image_tag` |
