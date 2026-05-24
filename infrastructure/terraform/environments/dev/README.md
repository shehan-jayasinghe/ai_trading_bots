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
| ECR repos (`deriv-backend`, `deriv-workers`, `deriv-frontend`) | `modules/ecr` |

## Apply

```bash
cd infrastructure/terraform/environments/dev
terraform init
terraform plan
terraform apply
```

EKS first apply can take **15–25 minutes**.

## After apply — EKS

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
| `eks_cluster_version` | `1.31` | Match AWS supported versions in region |
| `eks_node_instance_types` | `["t3.medium"]` | Dev node group |
| `ecr_repository_names` | backend, workers, frontend | Image repos for CI |

## Region

`us-west-1`

## Security

- Do not commit `.aws/credentials` or SSH private keys
- Jenkins EC2 IAM can describe EKS and push to ECR (for CI later)
