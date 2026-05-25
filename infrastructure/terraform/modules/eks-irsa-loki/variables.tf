variable "cluster_name" {
  description = "EKS cluster name (IAM role name prefix)"
  type        = string
}

variable "oidc_provider_arn" {
  description = "EKS OIDC provider ARN for IRSA"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket used by Loki"
  type        = string
}

variable "tags" {
  description = "Tags applied to IAM resources"
  type        = map(string)
  default     = {}
}
