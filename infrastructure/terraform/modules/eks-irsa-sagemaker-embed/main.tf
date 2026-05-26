module "irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.48"

  role_name = "${var.cluster_name}-workers-rag"

  role_policy_arns = merge(
    { sagemaker_embed = var.invoke_policy_arn },
    var.s3vectors_invoke_policy_arn != "" ? { s3vectors_rag = var.s3vectors_invoke_policy_arn } : {},
  )

  oidc_providers = {
    main = {
      provider_arn               = var.oidc_provider_arn
      namespace_service_accounts = ["${var.namespace}:${var.service_account_name}"]
    }
  }

  tags = var.tags
}
