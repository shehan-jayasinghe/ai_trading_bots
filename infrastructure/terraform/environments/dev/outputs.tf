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
