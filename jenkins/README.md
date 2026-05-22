# Jenkins CI — build images to ECR (dev)

Phase 1: **build and push only** (no EKS deploy yet).

## Pipelines

| Job (create in Jenkins UI) | Script path |
|----------------------------|-------------|
| `deriv-build-backend` | `jenkins/pipelines/build-backend.Jenkinsfile` |
| `deriv-build-workers` | `jenkins/pipelines/build-workers.Jenkinsfile` |
| `deriv-build-frontend` | `jenkins/pipelines/build-frontend.Jenkinsfile` |

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
   | `ECR_REGISTRY` | ECR host from `terraform output ecr_repository_urls` (no `/deriv-backend` suffix) |
   | `AWS_REGION` | `us-west-1` |

   Optional override per job: `jenkins/config/dev.env` in workspace (`jenkins/config/dev.env.example`).

## Create each Pipeline job

1. **New Item** → **Pipeline** → name `deriv-build-backend`  
2. **Pipeline** → Definition: **Pipeline script from SCM**  
3. SCM: your Git repo, branch `*/main` (or multibranch)  
4. **Script Path:** `jenkins/pipelines/build-backend.Jenkinsfile`  
5. Repeat for `deriv-build-workers` with `build-workers.Jenkinsfile`  
6. Repeat for `deriv-build-frontend` with `build-frontend.Jenkinsfile`

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

## Later (phase 2)

Deploy jobs: `deriv-deploy-backend`, `deriv-deploy-workers` (Helm/kubectl + `IMAGE_TAG` parameter).
