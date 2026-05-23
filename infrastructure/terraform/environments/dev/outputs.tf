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
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "eks_configure_kubectl" {
  value = module.eks.configure_kubectl_command
}

output "eks_oidc_provider_arn" {
  value = module.eks.oidc_provider_arn
}

output "ecr_repository_urls" {
  value = module.ecr.repository_urls
}

output "app_url" {
  description = "Public frontend URL (after EKS ingress + external-dns)"
  value       = "https://${var.app_domain}"
}

output "api_url" {
  description = "Public backend API URL (after EKS ingress + external-dns)"
  value       = "https://${var.api_domain}"
}

output "app_acm_certificate_arn" {
  description = "ACM certificate ARN for app_domain (Helm ingress)"
  value       = module.acm_app.certificate_arn
}

output "api_acm_certificate_arn" {
  description = "ACM certificate ARN for api_domain (Helm ingress)"
  value       = module.acm_api.certificate_arn
}

output "aws_lb_controller_role_arn" {
  description = "IRSA role ARN for aws-load-balancer-controller (Ansible eks.yml)"
  value       = module.eks_alb_controller_irsa.iam_role_arn
}

output "external_dns_role_arn" {
  description = "IRSA role ARN for external-dns (Ansible eks.yml)"
  value       = module.eks_external_dns_irsa.iam_role_arn
}
