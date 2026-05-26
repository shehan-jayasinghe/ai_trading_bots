variable "enable_sagemaker_embedding" {
  description = "If true (and enable_eks), deploy serverless SageMaker embedding endpoint + workers IRSA"
  type        = bool
  default     = true
}

variable "sagemaker_embedding_hf_model_id" {
  description = "Open-source Hugging Face model for trade-context embeddings"
  type        = string
  default     = "sentence-transformers/all-MiniLM-L6-v2"
}

variable "sagemaker_workers_namespace" {
  description = "K8s namespace for deriv-workers service account (must match Helm deriv-apps)"
  type        = string
  default     = "deriv-dev"
}

variable "sagemaker_workers_service_account" {
  description = "K8s service account name for planner/executor IRSA"
  type        = string
  default     = "deriv-workers"
}

variable "enable_s3vectors_bucket" {
  description = "If true, create S3 Vectors bucket + index for RAG"
  type        = bool
  default     = true
}

variable "s3vectors_index_name" {
  description = "S3 Vectors index name for trade embeddings"
  type        = string
  default     = "trade-embeddings"
}

variable "s3vectors_embedding_dimension" {
  description = "Vector dimension (must match SageMaker all-MiniLM-L6-v2)"
  type        = number
  default     = 384
}
