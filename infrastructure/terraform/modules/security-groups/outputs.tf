output "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "jenkins_ec2_security_group_id" {
  description = "Security group ID for Jenkins EC2"
  value       = aws_security_group.jenkins_ec2.id
}
