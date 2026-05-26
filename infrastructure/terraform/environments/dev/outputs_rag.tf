output "s3vectors_rag_bucket_name" {
  description = "S3 Vectors bucket name for RAG"
  value       = var.enable_s3vectors_bucket ? module.s3vectors_rag[0].vector_bucket_name : null
}

output "s3vectors_rag_bucket_arn" {
  description = "S3 Vectors bucket ARN"
  value       = var.enable_s3vectors_bucket ? module.s3vectors_rag[0].vector_bucket_arn : null
}

output "s3vectors_rag_index_name" {
  description = "S3 Vectors index name for trade embeddings"
  value       = var.enable_s3vectors_bucket ? module.s3vectors_rag_index[0].index_name : null
}

output "s3vectors_rag_index_arn" {
  description = "S3 Vectors index ARN"
  value       = var.enable_s3vectors_bucket ? module.s3vectors_rag_index[0].index_arn : null
}

output "sagemaker_embedding_endpoint_name" {
  description = "SageMaker embedding endpoint name (set SAGEMAKER_EMBEDDING_ENDPOINT for workers)"
  value       = var.enable_eks && var.enable_sagemaker_embedding ? module.sagemaker_embedding[0].endpoint_name : null
}

output "sagemaker_embedding_hf_model_id" {
  description = "Hugging Face model ID on the embedding endpoint"
  value       = var.enable_eks && var.enable_sagemaker_embedding ? module.sagemaker_embedding[0].hf_model_id : null
}

output "sagemaker_workers_irsa_role_arn" {
  description = "IRSA role ARN — annotate Helm serviceAccount deriv-workers (eks.amazonaws.com/role-arn)"
  value       = var.enable_eks && var.enable_sagemaker_embedding ? module.eks_workers_sagemaker_irsa[0].iam_role_arn : null
}
