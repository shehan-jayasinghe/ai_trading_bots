data "aws_caller_identity" "current" {}

module "loki_s3" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/loki-s3"

  bucket_name           = "${local.eks_cluster_name}-loki-${data.aws_caller_identity.current.account_id}"
  lifecycle_expire_days = var.loki_s3_lifecycle_expire_days
  tags                  = local.common_tags
}

module "eks_loki_irsa" {
  count = var.enable_eks ? 1 : 0

  source = "../../modules/eks-irsa-loki"

  cluster_name      = module.eks[0].cluster_name
  oidc_provider_arn = module.eks[0].oidc_provider_arn
  s3_bucket_arn     = module.loki_s3[0].bucket_arn
  tags              = local.common_tags
}
