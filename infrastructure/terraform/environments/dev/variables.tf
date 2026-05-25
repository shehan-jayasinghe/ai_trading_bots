variable "aws_region" {
  type    = string
  default = "us-west-1"
}

variable "project_name" {
  type    = string
  default = "deriv-ai-bot"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "enable_eks" {
  description = "If true, create EKS cluster, node group, IRSA, Loki S3/IRSA, and app/grafana ACM certs. If false, Jenkins + VPC + ECR only."
  type        = bool
  default     = true
}

variable "vpc_name" {
  type    = string
  default = "deriv-ai-dev"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "availability_zones" {
  type    = list(string)
  default = ["us-west-1a", "us-west-1c"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "single_nat_gateway" {
  type    = bool
  default = true
}

variable "public_key" {
  description = "SSH public key for Jenkins EC2 (contents of *.pub file)"
  type        = string
}

variable "root_domain" {
  description = "Existing Route53 hosted zone (e.g. testenvlab.shop)"
  type        = string
  default     = "testenvlab.shop"
}

variable "jenkins_domain" {
  description = "Jenkins FQDN (e.g. jenkins.testenvlab.shop)"
  type        = string
  default     = "jenkins.testenvlab.shop"
}

variable "app_domain" {
  description = "Public frontend URL host (e.g. app.testenvlab.shop)"
  type        = string
  default     = "app.testenvlab.shop"
}

variable "api_domain" {
  description = "Public backend API URL host (e.g. api.testenvlab.shop)"
  type        = string
  default     = "api.testenvlab.shop"
}

variable "grafana_domain" {
  description = "Public Grafana URL host (e.g. grafana.testenvlab.shop)"
  type        = string
  default     = "grafana.testenvlab.shop"
}

variable "jenkins_instance_type" {
  type    = string
  default = "t3.medium"
}

variable "ami_id" {
  description = "AMI ID for Jenkins EC2 instance"
  type        = string
}

variable "alb_name" {
  type    = string
  default = "deriv-jenkins-dev-alb"
}

variable "eks_cluster_version" {
  description = "Kubernetes version for EKS control plane (must be supported in region; upgrade one minor at a time from existing cluster)"
  type        = string
  default     = "1.31"
}

variable "eks_node_instance_types" {
  type    = list(string)
  default = ["t3.medium"]
}

variable "eks_node_desired_size" {
  description = "EKS managed node group desired capacity (use 2+ for platform + Grafana/Loki on dev)"
  type        = number
  default     = 2
}

variable "eks_node_min_size" {
  description = "0 allows park-platform to scale nodes to zero without terraform destroy"
  type        = number
  default     = 0
}

variable "eks_node_max_size" {
  type    = number
  default = 2
}

variable "loki_s3_lifecycle_expire_days" {
  description = "S3 lifecycle expiration for Loki log chunks (days)"
  type        = number
  default     = 90
}

variable "ecr_repository_names" {
  description = "ECR repositories for application images"
  type        = list(string)
  default = [
    "deriv-backend",
    "deriv-workers",
    "deriv-frontend",
  ]
}
