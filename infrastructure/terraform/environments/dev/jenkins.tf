# Jenkins CI host, ALB, ACM (jenkins), and Route53.

module "acm" {
  source = "../../modules/acm"

  domain_name    = var.jenkins_domain
  hosted_zone_id = data.aws_route53_zone.root.zone_id
  tags           = local.common_tags
}

module "jenkins_host" {
  source = "../../modules/jenkins-host"

  name               = "${var.project_name}-jenkins-${var.environment}"
  vpc_id             = module.vpc.vpc_id
  subnet_id          = module.vpc.public_subnets[0]
  public_key         = var.public_key
  ami_id             = var.ami_id
  security_group_ids = [module.security_groups.jenkins_ec2_security_group_id]
  instance_type      = var.jenkins_instance_type
  enable_eks         = var.enable_eks
  eks_cluster_arn    = var.enable_eks ? module.eks[0].cluster_arn : ""
  secrets_manager_secret_arns = [
    aws_secretsmanager_secret.platform.arn,
    aws_secretsmanager_secret.grafana.arn,
  ]
  tags = local.common_tags
}

module "alb_target_group" {
  source = "../../modules/alb-target-group"

  name               = "deriv-jenkins-dev-tg"
  vpc_id             = module.vpc.vpc_id
  target_instance_id = module.jenkins_host.instance_id
  tags               = local.common_tags
}

module "alb" {
  source = "../../modules/alb"

  name               = var.alb_name
  security_group_ids = [module.security_groups.alb_security_group_id]
  subnet_ids         = module.vpc.public_subnets
  target_group_arn   = module.alb_target_group.target_group_arn
  certificate_arn    = module.acm.certificate_arn
  tags               = local.common_tags
}

module "jenkins_dns" {
  source = "../../modules/route53-record"

  hosted_zone_id = data.aws_route53_zone.root.zone_id
  record_name    = var.jenkins_domain
  alb_dns_name   = module.alb.dns_name
  alb_zone_id    = module.alb.zone_id
}
