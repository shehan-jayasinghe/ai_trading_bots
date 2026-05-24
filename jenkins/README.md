# Jenkins CI — build images to ECR and deploy to EKS (dev)

## Pipelines

| Job (create in Jenkins UI) | Script path |
|----------------------------|-------------|
| `deriv-build-backend` | `jenkins/pipelines/build-backend.Jenkinsfile` |
| `deriv-build-workers` | `jenkins/pipelines/build-workers.Jenkinsfile` |
| `deriv-build-frontend` | `jenkins/pipelines/build-frontend.Jenkinsfile` |
| `deriv-deploy-platform` | `jenkins/pipelines/deploy-platform.Jenkinsfile` |

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
   | `APP_ACM_CERTIFICATE_ARN` | `terraform output -raw app_acm_certificate_arn` |
   | `API_ACM_CERTIFICATE_ARN` | `terraform output -raw api_acm_certificate_arn` |
   | `APP_DOMAIN` | `app.testenvlab.shop` |
   | `API_DOMAIN` | `api.testenvlab.shop` |
   | `PLATFORM_SECRET_ID` | `terraform output -raw platform_secret_name` |

   Optional override per job: copy `jenkins/config/dev.env.example` → `jenkins/config/dev.env` (gitignored).

4. **Platform secrets (once):** after `terraform apply`:

   ```bash
   cd infrastructure/terraform/environments/dev
   terraform output -raw platform_secret_populate_command
   # Edit CHANGE_ME values, then run the command
   ```

## Create each Pipeline job

1. **New Item** → **Pipeline** → name `deriv-build-backend`  
2. **Pipeline** → Definition: **Pipeline script from SCM**  
3. SCM: your Git repo, branch `*/main` (or multibranch)  
4. **Script Path:** `jenkins/pipelines/build-backend.Jenkinsfile`  
5. Repeat for `deriv-build-workers` with `build-workers.Jenkinsfile`  
6. Repeat for `deriv-build-frontend` with `build-frontend.Jenkinsfile`
7. **Deploy:** New Item → Pipeline → `deriv-deploy-platform` → Script Path: `jenkins/pipelines/deploy-platform.Jenkinsfile`  
   Enable **This project is parameterized** (pipeline defines `IMAGE_TAG`).

## Image tags

```text
<branch-sanitized>-<git-short-sha>   e.g. main-a1b2c3d
```

On branch `main`, also pushes `:latest`.

## Verify

```bash
aws ecr describe-images --repository-name deriv-backend --region us-west-1
aws ecr describe-images --repository-name deriv-workers --region us-west-1
aws ecr describe-images --repository-name deriv-frontend --region us-west-1
```

## Deploy to EKS (`deriv-deploy-platform`)

**Prerequisites:** `terraform apply` (includes Secrets Manager secret + Jenkins IAM), populate platform secret, first-time `ansible-playbook playbooks/eks-platform.yml` (ALB controller, optional if Jenkins deploy syncs secrets).

1. Build and push all images (or use the same tag for all three repos).
2. Run **deriv-deploy-platform** with parameter **`IMAGE_TAG`** (e.g. `master-ce74e1d` from build console, not `latest` unless pushed).
3. Deploy reads **AWS Secrets Manager** → syncs K8s secret → Helm upgrade.

Verify:

```bash
kubectl get pods -n deriv-dev
curl -sS https://api.testenvlab.shop/hello
```

Optional: trigger deploy after each build with **Trigger parameterized build** passing `IMAGE_TAG` from the build job.

## Later

Per-service deploy (`deriv-deploy-backend`, …) needs split `backend.image.tag` / `workers.image.tag` in Helm.
