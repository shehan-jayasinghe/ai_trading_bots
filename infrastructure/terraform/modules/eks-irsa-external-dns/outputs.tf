output "iam_role_arn" {
  description = "IAM role ARN for external-dns service account"
  value       = module.irsa.iam_role_arn
}

output "iam_role_name" {
  description = "IAM role name for external-dns"
  value       = module.irsa.iam_role_name
}
