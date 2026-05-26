output "platform_secret_name" {
  description = "AWS Secrets Manager secret name for platform credentials"
  value       = aws_secretsmanager_secret.platform.name
}

output "platform_secret_arn" {
  description = "AWS Secrets Manager secret ARN for platform credentials"
  value       = aws_secretsmanager_secret.platform.arn
}

output "grafana_secret_name" {
  description = "AWS Secrets Manager secret name for Grafana admin credentials"
  value       = aws_secretsmanager_secret.grafana.name
}

output "grafana_secret_arn" {
  description = "AWS Secrets Manager secret ARN for Grafana admin credentials"
  value       = aws_secretsmanager_secret.grafana.arn
}

output "platform_secret_populate_command" {
  description = "Run once to store platform secrets (replace placeholder values)"
  value       = <<-EOT
    aws secretsmanager put-secret-value \
      --region ${var.aws_region} \
      --secret-id ${aws_secretsmanager_secret.platform.name} \
      --secret-string '{"POSTGRES_PASSWORD":"CHANGE_ME","AUTH_SECRET":"CHANGE_ME","SAGEMAKER_EMBEDDING_ENDPOINT":"${try(module.sagemaker_embedding[0].endpoint_name, "")}","S3_VECTORS_BUCKET_NAME":"${try(module.s3vectors_rag[0].vector_bucket_name, "")}","S3_VECTORS_INDEX_NAME":"${try(module.s3vectors_rag_index[0].index_name, "")}","BEDROCK_REGION":"${var.aws_region}","BEDROCK_DECISION_MODEL_ID":"amazon.nova-micro-v1:0"}'
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
