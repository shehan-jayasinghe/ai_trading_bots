output "loki_s3_bucket" {
  description = "S3 bucket for Loki log storage (long-term; used by Grafana/Loki on EKS)"
  value       = var.enable_eks ? module.loki_s3[0].bucket_id : null
}

output "loki_role_arn" {
  description = "IRSA role ARN for Loki service account (monitoring:loki)"
  value       = var.enable_eks ? module.eks_loki_irsa[0].iam_role_arn : null
}
