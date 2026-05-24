output "iam_role_name" {
  description = "IAM role name attached to the Jenkins EC2 instance"
  value       = aws_iam_role.jenkins.name
}

output "iam_role_arn" {
  description = "IAM role ARN attached to the Jenkins EC2 instance (for EKS access entries)"
  value       = aws_iam_role.jenkins.arn
}

output "instance_id" {
  description = "Jenkins EC2 instance ID"
  value       = aws_instance.jenkins.id
}

output "public_ip" {
  description = "Jenkins EC2 public IP"
  value       = aws_instance.jenkins.public_ip
}

output "private_ip" {
  description = "Jenkins EC2 private IP"
  value       = aws_instance.jenkins.private_ip
}

output "key_pair_name" {
  description = "AWS key pair name for SSH"
  value       = aws_key_pair.jenkins.key_name
}

output "ssh_command" {
  description = "Example SSH command (use matching private key file)"
  value       = "ssh -i <private-key> ubuntu@${aws_instance.jenkins.public_ip}"
}

output "initial_admin_password_command" {
  description = "Run over SSH to get Jenkins unlock password"
  value       = "sudo cat /var/lib/jenkins/secrets/initialAdminPassword"
}
