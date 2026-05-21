output "target_group_arn" {
  description = "ALB target group ARN"
  value       = aws_lb_target_group.jenkins.arn
}
