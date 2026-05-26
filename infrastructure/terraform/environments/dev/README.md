# Dev infrastructure (Terraform)

**Terraform** = AWS infra (VPC, Jenkins EC2, ALB, **EKS**, **ECR**)  
**Ansible** = Jenkins on EC2 + later Postgres/Kafka/apps on EKS

## What Terraform provisions

| Resource | Module |
|----------|--------|
| VPC + NAT + EKS subnet tags | `modules/vpc` |
| Jenkins EC2 + IAM (ECR + EKS read) | `modules/jenkins-host` |
| ALB + ACM + Route53 | `alb`, `acm`, `route53-record` |
| EKS cluster + managed node group | `modules/eks` |
| EBS CSI driver add-on + IRSA | `modules/eks-irsa-ebs-csi`, `aws_eks_addon.ebs_csi` |
| Loki log storage (S3) + IRSA | `modules/loki-s3`, `modules/eks-irsa-loki` |
| SageMaker **serverless** embedding endpoint (HF `all-MiniLM-L6-v2`) + workers IRSA | `modules/sagemaker-embedding`, `modules/eks-irsa-sagemaker-embed` |
| S3 Vectors bucket (RAG storage) | `modules/s3vectors-bucket` (`enable_s3vectors_bucket`) |
| ECR repos (`deriv-backend`, `deriv-workers`, `deriv-frontend`) | `modules/ecr` |

## Root `.tf` layout (one state, split by concern)

| File | Contents |
|------|----------|
| `providers.tf` | Terraform/providers (`aws`, `awscc`), shared `locals`, Route53 zone |
| `data.tf` | Shared data sources (`aws_caller_identity`) |
| `variables_*.tf` | Inputs: `core`, `eks`, `monitoring`, `rag` |
| `network.tf` | VPC, security groups |
| `jenkins.tf` | Jenkins EC2, ALB, ACM (jenkins), DNS |
| `ecr.tf` | ECR repositories |
| `eks.tf` | EKS cluster, IRSA (ALB controller, external-dns, EBS CSI), Jenkins cluster access |
| `platform_acm.tf` | ACM for app / api / grafana (when `enable_eks`) |
| `secrets.tf` | Secrets Manager shells |
| `monitoring.tf` | Loki S3 + Loki IRSA |
| `rag.tf` | SageMaker embedding, S3 Vectors bucket + index, workers IRSA |
| `outputs_*.tf` | Outputs grouped like variables |
| `terraform.tfvars` | Environment values |

## Apply

```bash
cd infrastructure/terraform/environments/dev
terraform init
terraform plan
terraform apply
```

EKS first apply can take **15–25 minutes** when `enable_eks = true`.

### Jenkins-only mode (`enable_eks = false`)

Set in `terraform.tfvars`:

```hcl
enable_eks = false
```

Creates VPC, Jenkins, ALB, ECR, and Secrets Manager shells — **no** EKS control plane, node group, IRSA, or platform ACM certs. Use this to save cost while setting up CI; set `enable_eks = true` and apply again when ready to deploy to Kubernetes.

## After apply — EKS

Skip this section when `enable_eks = false` (`terraform output enable_eks`).

```bash
terraform output -raw eks_configure_kubectl
# runs: aws eks update-kubeconfig --region us-west-1 --name deriv-ai-bot-dev

kubectl get nodes
kubectl get pods -A
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-ebs-csi-driver
```

EBS CSI (required for Helm `gp2` PVCs):

```bash
aws eks describe-addon --cluster-name deriv-ai-bot-dev --addon-name aws-ebs-csi-driver --region us-west-1 --query addon.status --output text
```

ECR URLs:

```bash
terraform output ecr_repository_urls
```

## After apply — Jenkins

See `infrastructure/ansible/README.md` for Ansible install and unlock password.

| Output | Use |
|--------|-----|
| `jenkins_url` | https://jenkins.testenvlab.shop |
| `jenkins_public_ip` | SSH / Ansible |
| `eks_cluster_name` | Ansible / Jenkins pipelines |

## Variables (`terraform.tfvars`)

| Variable | Default | Notes |
|----------|---------|--------|
| `enable_eks` | `true` | `false` = Jenkins + VPC + ECR only (no cluster, no Loki S3, no app/grafana ACM) |
| `eks_cluster_version` | `1.31` | Match AWS supported versions in region |
| `eks_node_instance_types` | `["t2.medium"]` | Dev node group |
| `eks_node_desired_size` | `5` in `terraform.tfvars` | Platform + monitoring headroom (pod limits per node) |
| `eks_node_min_size` | `0` | Allows **park-platform** to scale nodes to zero |
| `eks_node_max_size` | `5` | Must be ≥ `eks_node_desired_size`; matches wake Jenkins globals |
| `ecr_repository_names` | backend, workers, frontend | Image repos for CI |

## Region

`us-west-1`

## Security

- Do not commit `.aws/credentials` or SSH private keys
- Jenkins EC2 IAM can describe EKS and push to ECR (for CI later)
