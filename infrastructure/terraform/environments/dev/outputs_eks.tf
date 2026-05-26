output "eks_cluster_name" {
  value = var.enable_eks ? module.eks[0].cluster_name : null
}

output "eks_cluster_endpoint" {
  value = var.enable_eks ? module.eks[0].cluster_endpoint : null
}

output "eks_configure_kubectl" {
  value = var.enable_eks ? module.eks[0].configure_kubectl_command : null
}

output "eks_oidc_provider_arn" {
  value = var.enable_eks ? module.eks[0].oidc_provider_arn : null
}

output "app_url" {
  description = "Public frontend URL (after EKS ingress + external-dns)"
  value       = var.enable_eks ? "https://${var.app_domain}" : null
}

output "api_url" {
  description = "Public backend API URL (after EKS ingress + external-dns)"
  value       = var.enable_eks ? "https://${var.api_domain}" : null
}

output "app_acm_certificate_arn" {
  description = "ACM certificate ARN for app_domain (Helm ingress)"
  value       = var.enable_eks ? module.acm_app[0].certificate_arn : null
}

output "api_acm_certificate_arn" {
  description = "ACM certificate ARN for api_domain (Helm ingress)"
  value       = var.enable_eks ? module.acm_api[0].certificate_arn : null
}

output "grafana_url" {
  description = "Public Grafana URL (after eks-monitoring ingress + external-dns)"
  value       = var.enable_eks ? "https://${var.grafana_domain}" : null
}

output "grafana_acm_certificate_arn" {
  description = "ACM certificate ARN for grafana_domain (Helm Grafana ingress)"
  value       = var.enable_eks ? module.acm_grafana[0].certificate_arn : null
}

output "aws_lb_controller_role_arn" {
  description = "IRSA role ARN for aws-load-balancer-controller (Helm eks-cluster-addons)"
  value       = var.enable_eks ? module.eks_alb_controller_irsa[0].iam_role_arn : null
}

output "external_dns_role_arn" {
  description = "IRSA role ARN for external-dns (Helm eks-cluster-addons)"
  value       = var.enable_eks ? module.eks_external_dns_irsa[0].iam_role_arn : null
}

output "ebs_csi_driver_role_arn" {
  description = "IRSA role ARN for aws-ebs-csi-driver (installed via Terraform EKS add-on)"
  value       = var.enable_eks ? module.eks_ebs_csi_irsa[0].iam_role_arn : null
}

output "ebs_csi_addon_arn" {
  description = "ARN of aws-ebs-csi-driver EKS add-on (status via aws eks describe-addon)"
  value       = var.enable_eks ? aws_eks_addon.ebs_csi[0].arn : null
}
