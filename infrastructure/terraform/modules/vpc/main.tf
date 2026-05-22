locals {
  eks_public_subnet_tags = var.eks_cluster_name != "" ? {
    "kubernetes.io/role/elb"                          = "1"
    "kubernetes.io/cluster/${var.eks_cluster_name}"   = "shared"
  } : {}

  eks_private_subnet_tags = var.eks_cluster_name != "" ? {
    "kubernetes.io/role/internal-elb"                 = "1"
    "kubernetes.io/cluster/${var.eks_cluster_name}"   = "shared"
  } : {}
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = var.name
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway   = true
  single_nat_gateway   = var.single_nat_gateway
  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags  = local.eks_public_subnet_tags
  private_subnet_tags = local.eks_private_subnet_tags

  tags = var.tags
}
