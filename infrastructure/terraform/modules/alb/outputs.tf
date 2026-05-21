output "dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.jenkins.dns_name
}

output "zone_id" {
  description = "ALB hosted zone ID (for Route53 alias)"
  value       = aws_lb.jenkins.zone_id
}

output "arn" {
  description = "ALB ARN"
  value       = aws_lb.jenkins.arn
}
