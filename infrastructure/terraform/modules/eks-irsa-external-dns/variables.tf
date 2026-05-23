variable "cluster_name" {
  description = "EKS cluster name (used for IAM role naming)"
  type        = string
}

variable "oidc_provider_arn" {
  description = "EKS OIDC provider ARN for IRSA"
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID external-dns may manage"
  type        = string
}

variable "tags" {
  description = "Tags applied to IAM resources"
  type        = map(string)
  default     = {}
}
