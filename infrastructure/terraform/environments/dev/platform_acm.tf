# ACM certificates for EKS ingress (app, API, Grafana). Requires enable_eks.

module "acm_app" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/acm"

  domain_name    = var.app_domain
  hosted_zone_id = data.aws_route53_zone.root.zone_id
  tags           = local.common_tags
}

module "acm_api" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/acm"

  domain_name    = var.api_domain
  hosted_zone_id = data.aws_route53_zone.root.zone_id
  tags           = local.common_tags
}

module "acm_grafana" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/acm"

  domain_name    = var.grafana_domain
  hosted_zone_id = data.aws_route53_zone.root.zone_id
  tags           = local.common_tags
}
