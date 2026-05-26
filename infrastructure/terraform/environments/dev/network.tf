# VPC and security groups (foundation for Jenkins + EKS).

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
