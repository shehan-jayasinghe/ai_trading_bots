# Park and wake (reduce AWS cost without destroy)

## When to use

| Goal | Action |
|------|--------|
| Not using app for days, keep DB/Kafka on PVCs | **Park** → **Wake** |
| Remove everything from AWS | **Teardown** → `terraform destroy` |
| Daily coding only | **local-env/docker-compose** (no EKS) |

## Park (`deriv-park-platform`)

1. Scales platform + monitoring workloads to **0** replicas (Helm release stays installed).
2. Deletes **Ingress** and any remaining **k8s ALB** in `VPC_ID`.
3. Sets EKS node group **desiredSize=0** (requires `eks_node_min_size = 0` in Terraform).
4. Optionally **stops** Jenkins EC2 (`deriv-ai-bot-jenkins-dev` tag).

## Wake (`deriv-wake-platform`)

1. Starts Jenkins EC2 if stopped.
2. Scales node group to **1** (configurable via `EKS_NODE_DESIRED_SIZE`).
3. Runs full **`deriv-deploy-platform`** Helm flow (restores pods, Ingress, monitoring if enabled).

## What still costs money while parked

- EKS **control plane** (~$73/month if cluster exists 24/7)
- **NAT gateway** (~$32/month)
- **Jenkins ALB** (if Jenkins Terraform stack is up)
- **EBS** PVCs (Postgres, Kafka, Grafana, Loki)

## Terraform

```bash
cd infrastructure/terraform/environments/dev
terraform apply   # applies eks_node_min_size=0 and Jenkins park/wake IAM
```

## Manual

```bash
export AWS_REGION=us-west-1 EKS_CLUSTER_NAME=deriv-ai-bot-dev VPC_ID=<vpc-id>
bash jenkins/scripts/park-platform.sh

# later
export ECR_REGISTRY=... IMAGE_TAG=latest  # plus deploy env vars for wake
bash jenkins/scripts/wake-platform.sh
```
