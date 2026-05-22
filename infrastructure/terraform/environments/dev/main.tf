module "vpc" {
  source = "../../modules/vpc"

  name                 = var.vpc_name
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  private_subnet_cidrs = var.private_subnet_cidrs
  public_subnet_cidrs  = var.public_subnet_cidrs
  single_nat_gateway   = var.single_nat_gateway
  eks_cluster_name     = local.eks_cluster_name
  tags                 = local.common_tags
}

module "security_groups" {
  source = "../../modules/security-groups"

  name_prefix = "${var.project_name}-${var.environment}"
  vpc_id      = module.vpc.vpc_id
  tags        = local.common_tags
}

module "acm" {
  source = "../../modules/acm"

  domain_name    = var.jenkins_domain
  hosted_zone_id = data.aws_route53_zone.root.zone_id
  tags           = local.common_tags
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

module "ecr" {
  source = "../../modules/ecr"

  repository_names = var.ecr_repository_names
  tags             = local.common_tags
}

module "eks" {
  source = "../../modules/eks"

  cluster_name        = local.eks_cluster_name
  cluster_version     = var.eks_cluster_version
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = concat(module.vpc.public_subnets, module.vpc.private_subnets)
  node_subnet_ids     = module.vpc.private_subnets
  node_instance_types = var.eks_node_instance_types
  node_desired_size   = var.eks_node_desired_size
  node_min_size       = var.eks_node_min_size
  node_max_size       = var.eks_node_max_size
  tags                = local.common_tags
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
  eks_cluster_arn    = module.eks.cluster_arn
  tags               = local.common_tags
}
