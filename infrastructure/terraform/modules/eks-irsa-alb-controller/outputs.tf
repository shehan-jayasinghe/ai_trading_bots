output "iam_role_arn" {
  description = "IAM role ARN for aws-load-balancer-controller service account"
  value       = module.irsa.iam_role_arn
}

output "iam_role_name" {
  description = "IAM role name for aws-load-balancer-controller"
  value       = module.irsa.iam_role_name
}
