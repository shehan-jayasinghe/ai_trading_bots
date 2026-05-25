# Jenkins CI — build images to ECR and deploy to EKS (dev)

## Pipelines

| Job (create in Jenkins UI) | Script path |
|----------------------------|-------------|
| `deriv-build-backend` | `jenkins/pipelines/build-backend.Jenkinsfile` |
| `deriv-build-workers` | `jenkins/pipelines/build-workers.Jenkinsfile` |
| `deriv-build-frontend` | `jenkins/pipelines/build-frontend.Jenkinsfile` |
| `deriv-deploy-platform` | `jenkins/pipelines/deploy-platform.Jenkinsfile` |
| `deriv-teardown-platform-aws` | `jenkins/pipelines/teardown-platform-aws.Jenkinsfile` |
| `deriv-park-platform` | `jenkins/pipelines/park-platform.Jenkinsfile` |
| `deriv-wake-platform` | `jenkins/pipelines/wake-platform.Jenkinsfile` |

## One-time Jenkins setup

**Ansible** (`jenkins-host.yml`) installs Jenkins plus CI tools: Docker, AWS CLI, kubectl, Helm.

1. Run Ansible:

   ```bash
   ansible-playbook playbooks/jenkins-host.yml -vv
   ```

2. **Jenkins UI (once):** unlock → suggested plugins (Pipeline, Git) → admin user  

3. **Global environment variables** (Manage Jenkins → System → Global properties):

   | Name | Value |
   |------|--------|
   | `ECR_REGISTRY` | `terraform output -raw ecr_registry` |
   | `AWS_REGION` | `us-west-1` |
   | `EKS_CLUSTER_NAME` | `deriv-ai-bot-dev` |
   | `VPC_ID` | `terraform output -raw vpc_id` |
   | `ALB_CONTROLLER_ROLE_ARN` | `terraform output -raw alb_controller_role_arn` |
   | `EXTERNAL_DNS_ROLE_ARN` | `terraform output -raw external_dns_role_arn` |
   | `EXTERNAL_DNS_DOMAIN_FILTER` | `testenvlab.shop` |
   | `EXTERNAL_DNS_TXT_OWNER_ID` | `deriv-dev` |
   | `APP_ACM_CERTIFICATE_ARN` | `terraform output -raw app_acm_certificate_arn` |
   | `API_ACM_CERTIFICATE_ARN` | `terraform output -raw api_acm_certificate_arn` |
   | `APP_DOMAIN` | `app.testenvlab.shop` |
   | `API_DOMAIN` | `api.testenvlab.shop` |
   | `PLATFORM_SECRET_ID` | `terraform output -raw platform_secret_name` |
   | `LOKI_S3_BUCKET` | `terraform output -raw loki_s3_bucket` |
   | `LOKI_ROLE_ARN` | `terraform output -raw loki_role_arn` |
   | `GRAFANA_SECRET_ID` | `terraform output -raw grafana_secret_name` |
   | `GRAFANA_DOMAIN` | `grafana.testenvlab.shop` |
   | `GRAFANA_ACM_CERTIFICATE_ARN` | `terraform output -raw grafana_acm_certificate_arn` |

   Full list with terraform output hints: **`jenkins/global-env.example`** (reference only — set values in Jenkins UI, not on the server).

4. **Secrets (once):** after `terraform apply`:

   ```bash
   cd infrastructure/terraform/environments/dev
   terraform output -raw platform_secret_populate_command
   terraform output -raw grafana_secret_populate_command
   # Edit CHANGE_ME values, then run each command
   ```

## Create each Pipeline job

1. **New Item** → **Pipeline** → name `deriv-build-backend`  
2. **Pipeline** → Definition: **Pipeline script from SCM**  
3. SCM: your Git repo, branch `*/master` (or multibranch)  
4. **Script Path:** `jenkins/pipelines/build-backend.Jenkinsfile`  
5. Repeat for `deriv-build-workers` with `build-workers.Jenkinsfile`  
6. Repeat for `deriv-build-frontend` with `build-frontend.Jenkinsfile`
7. **Deploy:** New Item → Pipeline → `deriv-deploy-platform` → Script Path: `jenkins/pipelines/deploy-platform.Jenkinsfile`  
   Enable **This project is parameterized** (`IMAGE_TAG`, `DEPLOY_ADDONS`, `DEPLOY_MONITORING`, `HELM_DEBUG`).
8. **Teardown (before `terraform destroy`):** New Item → Pipeline → `deriv-teardown-platform-aws` → Script Path: `jenkins/pipelines/teardown-platform-aws.Jenkinsfile`
9. **Park / wake (save cost, keep Terraform):** `deriv-park-platform` / `deriv-wake-platform` — scale pods and nodes to **0**, drop k8s ALB, stop Jenkins EC2; wake scales nodes up and runs Helm deploy.

## Image tags

```text
<branch-sanitized>-<git-short-sha>   e.g. master-a1b2c3d
```

On branch `master` (or `main`), also pushes `:latest` to ECR.

## Verify

```bash
aws ecr describe-images --repository-name deriv-backend --region us-west-1
aws ecr describe-images --repository-name deriv-workers --region us-west-1
aws ecr describe-images --repository-name deriv-frontend --region us-west-1
```

## Deploy to EKS (`deriv-deploy-platform`)

**Prerequisites:** `terraform apply`, populate platform secret, Jenkins globals (see table above).

**Pipeline stages** (one job `deriv-deploy-platform`):

1. `deploy/preflight/platform-preflight.sh` — kubeconfig, EBS CSI, ECR tags  
2. `deploy/infrastructure/helm-eks-addons-deploy.sh` — chart `deploy/helm/eks-cluster-addons`  
3. `deploy/helm-platform-deploy.sh` — `deriv-postgres` → `deriv-kafka` → `deriv-apps` → `deriv-ingress`  
4. `deploy/monitoring/helm-monitoring-deploy.sh` — chart `deploy/helm/eks-monitoring` (optional)

1. Build and push all images (or use the same tag for all three repos).
2. Run **deriv-deploy-platform** with **`IMAGE_TAG=latest`** (after builds on `master`) or a specific tag e.g. `master-a1cf7f0`.
3. Deploy syncs **AWS Secrets Manager** → K8s secret inside `helm-platform-deploy.sh`.
4. **HELM_DEBUG** (default on): Helm `--debug` streams install/wait progress to the console and `helm-deploy.log` (archived on every run). On failure/abort, diagnostics print pod/events automatically.
5. **Helm lock**: each deploy runs `deploy_helm_unlock` (rollback or delete pending release secrets) before `helm upgrade` if a prior run was aborted.

Verify:

```bash
kubectl get pods -n deriv-dev
curl -sS https://api.testenvlab.shop/hello
```

Optional: trigger deploy after each build with **Trigger parameterized build** passing `IMAGE_TAG` from the build job.

## Logs in Grafana (platform deploy)

Platform deploy installs **eks-monitoring** chart when `DEPLOY_MONITORING=true` (default). Set `LOKI_S3_BUCKET` and `LOKI_ROLE_ARN` from Terraform outputs.

See [docs/08-monitoring-logs.md](../docs/08-monitoring-logs.md) for port-forward, LogQL, and admin password.

## Park and wake (no destroy)

Use when you are not using the lab for a while but want to keep Terraform state and data on EBS PVCs.

| Job | What it does |
|-----|----------------|
| **`deriv-park-platform`** | Scale all `deriv-dev` + `monitoring` Deployments/StatefulSets to **0**, delete Ingress (k8s ALB), scale EKS node group to **0**, optionally **stop** Jenkins EC2 |
| **`deriv-wake-platform`** | **Start** Jenkins, scale nodes up, run preflight + addons + platform + monitoring Helm scripts |

Requires **`eks_node_min_size = 0`** in Terraform (default in repo). After changing IAM, run **`terraform apply`** once.

**Still billed while parked:** EKS control plane (~$0.10/hr), NAT gateway, Jenkins ALB (if Jenkins stack exists), EBS volumes for Postgres/Kafka/Grafana.

**Scripts:** `jenkins/scripts/lifecycle/park-platform.sh`, `jenkins/scripts/lifecycle/wake-platform.sh` (see `jenkins/scripts/README.md`)

## Teardown before `terraform destroy` (`deriv-teardown-platform-aws`)

The platform **Ingress ALB** and related ENIs/EIPs are created by the **AWS Load Balancer Controller** in Kubernetes. They are **not** in Terraform state. If you run `terraform destroy` while that ALB still exists, destroy can fail (ACM “in use”, subnets/IGW dependencies).

**Order when recycling dev:**

1. Run **`deriv-teardown-platform-aws`** (uninstalls Helm releases when the cluster is up, then deletes `k8s-*` ALBs/target groups, waits for ELB ENIs, deletes `k8s-*` security groups left by the ALB controller, releases unattached EIPs).
2. Run **`terraform destroy`** from `infrastructure/terraform/environments/dev` (on your Mac or another runner with Terraform state).

Requires Jenkins globals: `VPC_ID`, `EKS_CLUSTER_NAME`, `AWS_REGION`. After changing Jenkins IAM in Terraform, run `terraform apply` once so the Jenkins EC2 role can call ELB/EC2 APIs.

Manual equivalent:

```bash
export AWS_REGION=us-west-1 VPC_ID=<vpc-id> EKS_CLUSTER_NAME=deriv-ai-bot-dev
bash jenkins/scripts/lifecycle/teardown-k8s-aws-orphans.sh
cd infrastructure/terraform/environments/dev && terraform destroy
```

## Later

Per-service deploy (`deriv-deploy-backend`, …) needs split `backend.image.tag` / `workers.image.tag` in Helm.
