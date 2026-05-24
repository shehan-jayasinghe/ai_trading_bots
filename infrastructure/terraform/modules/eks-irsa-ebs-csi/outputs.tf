output "iam_role_arn" {
  description = "IRSA role ARN for the aws-ebs-csi-driver EKS add-on"
  value       = module.irsa.iam_role_arn
}

output "iam_role_name" {
  description = "IAM role name for the EBS CSI driver"
  value       = module.irsa.iam_role_name
}
