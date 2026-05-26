# RAG / ML: SageMaker embeddings, S3 Vectors, workers IRSA.

module "s3vectors_rag" {
  count = var.enable_s3vectors_bucket ? 1 : 0

  source = "../../modules/s3vectors-bucket"

  vector_bucket_name = local.s3vectors_bucket_name
  tags               = local.common_tags
}

module "s3vectors_rag_index" {
  count = var.enable_s3vectors_bucket ? 1 : 0

  source = "../../modules/s3vectors-index"

  vector_bucket_name = local.s3vectors_bucket_name
  index_name         = var.s3vectors_index_name
  dimension          = var.s3vectors_embedding_dimension
  distance_metric    = "cosine"
  tags               = local.common_tags

  depends_on = [module.s3vectors_rag]
}

module "sagemaker_embedding" {
  count = var.enable_eks && var.enable_sagemaker_embedding ? 1 : 0

  source = "../../modules/sagemaker-embedding"

  name_prefix = "${var.project_name}-${var.environment}"
  aws_region  = var.aws_region
  hf_model_id = var.sagemaker_embedding_hf_model_id
  tags        = local.common_tags
}

module "eks_workers_sagemaker_irsa" {
  count = var.enable_eks && var.enable_sagemaker_embedding ? 1 : 0

  source = "../../modules/eks-irsa-sagemaker-embed"

  cluster_name                = module.eks[0].cluster_name
  oidc_provider_arn           = module.eks[0].oidc_provider_arn
  namespace                   = var.sagemaker_workers_namespace
  service_account_name        = var.sagemaker_workers_service_account
  invoke_policy_arn           = module.sagemaker_embedding[0].invoke_policy_arn
  s3vectors_invoke_policy_arn = var.enable_s3vectors_bucket ? module.s3vectors_rag_index[0].invoke_policy_arn : ""
  tags                        = local.common_tags
}
