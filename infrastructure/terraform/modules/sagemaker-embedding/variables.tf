variable "name_prefix" {
  description = "Prefix for SageMaker model and endpoint resources"
  type        = string
}

variable "aws_region" {
  description = "AWS region (used for Hugging Face DLC image URI)"
  type        = string
}

variable "hf_model_id" {
  description = "Hugging Face model ID (open-source; downloaded at endpoint startup)"
  type        = string
  default     = "sentence-transformers/all-MiniLM-L6-v2"
}

variable "inference_image_uri" {
  description = "Optional override for Hugging Face PyTorch inference DLC image"
  type        = string
  default     = ""
}

variable "serverless_memory_mb" {
  description = "SageMaker serverless inference memory (MB)"
  type        = number
  default     = 2048
}

variable "serverless_max_concurrency" {
  description = "Max concurrent invocations for serverless endpoint"
  type        = number
  default     = 2
}

variable "tags" {
  description = "Tags applied to SageMaker and IAM resources"
  type        = map(string)
  default     = {}
}
