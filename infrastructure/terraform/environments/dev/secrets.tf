# Platform app secrets (passwords, API keys). Values are NOT stored in Terraform state —
# populate once after apply (see output platform_secret_populate_command).

resource "aws_secretsmanager_secret" "platform" {
  name        = "${var.project_name}/${var.environment}/platform"
  description = "Platform secrets: POSTGRES_PASSWORD, AUTH_SECRET, OPENAI_API_KEY"
  tags        = local.common_tags
}

resource "aws_secretsmanager_secret" "grafana" {
  name        = "${var.project_name}/${var.environment}/grafana"
  description = "Grafana admin: GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD"
  tags        = local.common_tags
}
