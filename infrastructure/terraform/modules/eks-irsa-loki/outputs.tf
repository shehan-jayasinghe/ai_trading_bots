output "iam_role_arn" {
  description = "IRSA role ARN for Loki service account (monitoring:loki)"
  value       = module.irsa.iam_role_arn
}

output "iam_role_name" {
  value = module.irsa.iam_role_name
}
