# EKS cluster, add-ons, and IRSA for platform controllers.

module "eks" {
  count = var.enable_eks ? 1 : 0

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

resource "aws_security_group_rule" "eks_api_from_jenkins" {
  count = var.enable_eks ? 1 : 0

  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = module.eks[0].cluster_security_group_id
  source_security_group_id = module.security_groups.jenkins_ec2_security_group_id
  description              = "EKS API from Jenkins CI host"
}

module "eks_alb_controller_irsa" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/eks-irsa-alb-controller"

  cluster_name      = module.eks[0].cluster_name
  oidc_provider_arn = module.eks[0].oidc_provider_arn
  tags              = local.common_tags
}

module "eks_external_dns_irsa" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/eks-irsa-external-dns"

  cluster_name      = module.eks[0].cluster_name
  oidc_provider_arn = module.eks[0].oidc_provider_arn
  hosted_zone_id    = data.aws_route53_zone.root.zone_id
  tags              = local.common_tags
}

module "eks_ebs_csi_irsa" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/eks-irsa-ebs-csi"

  cluster_name      = module.eks[0].cluster_name
  oidc_provider_arn = module.eks[0].oidc_provider_arn
  tags              = local.common_tags
}

resource "aws_eks_addon" "ebs_csi" {
  count = var.enable_eks ? 1 : 0

  cluster_name                = module.eks[0].cluster_name
  addon_name                  = "aws-ebs-csi-driver"
  service_account_role_arn    = module.eks_ebs_csi_irsa[0].iam_role_arn
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = local.common_tags
}

resource "aws_eks_access_entry" "jenkins" {
  count = var.enable_eks ? 1 : 0

  cluster_name  = module.eks[0].cluster_name
  principal_arn = module.jenkins_host.iam_role_arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "jenkins_cluster_admin" {
  count = var.enable_eks ? 1 : 0

  cluster_name  = module.eks[0].cluster_name
  principal_arn = module.jenkins_host.iam_role_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_access_entry.jenkins]
}
