output "enable_eks" {
  description = "Whether EKS and related platform resources were created"
  value       = var.enable_eks
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "hosted_zone_id" {
  value = data.aws_route53_zone.root.zone_id
}

output "jenkins_instance_id" {
  value = module.jenkins_host.instance_id
}

output "jenkins_public_ip" {
  description = "Jenkins EC2 public IP"
  value       = module.jenkins_host.public_ip
}

output "jenkins_key_pair_name" {
  value = module.jenkins_host.key_pair_name
}

output "jenkins_url" {
  description = "Jenkins HTTPS URL (via ALB + ACM)"
  value       = "https://${var.jenkins_domain}"
}

output "jenkins_url_http" {
  description = "Jenkins HTTP URL (via ALB)"
  value       = "http://${var.jenkins_domain}"
}

output "alb_dns_name" {
  value = module.alb.dns_name
}

output "ssh_command" {
  value = module.jenkins_host.ssh_command
}

output "jenkins_private_ip" {
  description = "Jenkins EC2 private IP"
  value       = module.jenkins_host.private_ip
}

output "jenkins_unlock_password_command" {
  value = module.jenkins_host.initial_admin_password_command
}

output "ansible_install_command" {
  description = "Run after terraform apply to install Jenkins on EC2"
  value       = "cd infrastructure/ansible && ansible-galaxy collection install -r requirements.yml && ansible-playbook playbooks/jenkins-host.yml -vv"
}

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

output "ecr_repository_urls" {
  value = module.ecr.repository_urls
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

output "grafana_secret_name" {
  description = "AWS Secrets Manager secret name for Grafana admin credentials"
  value       = aws_secretsmanager_secret.grafana.name
}

output "grafana_secret_arn" {
  description = "AWS Secrets Manager secret ARN for Grafana admin credentials"
  value       = aws_secretsmanager_secret.grafana.arn
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

output "ecr_registry" {
  description = "ECR registry host (no repository suffix) for Jenkins dev.env"
  value       = split("/", module.ecr.repository_urls["deriv-backend"])[0]
}

output "platform_secret_name" {
  description = "AWS Secrets Manager secret name for platform credentials"
  value       = aws_secretsmanager_secret.platform.name
}

output "platform_secret_arn" {
  description = "AWS Secrets Manager secret ARN for platform credentials"
  value       = aws_secretsmanager_secret.platform.arn
}

output "loki_s3_bucket" {
  description = "S3 bucket for Loki log storage (long-term; used by Grafana/Loki on EKS)"
  value       = var.enable_eks ? module.loki_s3[0].bucket_id : null
}

output "loki_role_arn" {
  description = "IRSA role ARN for Loki service account (monitoring:loki)"
  value       = var.enable_eks ? module.eks_loki_irsa[0].iam_role_arn : null
}

output "platform_secret_populate_command" {
  description = "Run once to store platform secrets (replace placeholder values)"
  value       = <<-EOT
    aws secretsmanager put-secret-value \
      --region ${var.aws_region} \
      --secret-id ${aws_secretsmanager_secret.platform.name} \
      --secret-string '{"POSTGRES_PASSWORD":"CHANGE_ME","AUTH_SECRET":"CHANGE_ME","OPENAI_API_KEY":""}'
  EOT
}

output "grafana_secret_populate_command" {
  description = "Run once to store Grafana admin credentials (replace placeholder values)"
  value       = <<-EOT
    aws secretsmanager put-secret-value \
      --region ${var.aws_region} \
      --secret-id ${aws_secretsmanager_secret.grafana.name} \
      --secret-string '{"GRAFANA_ADMIN_USER":"admin","GRAFANA_ADMIN_PASSWORD":"CHANGE_ME"}'
  EOT
}
