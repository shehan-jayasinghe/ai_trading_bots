variable "cluster_name" {
  type = string
}

variable "oidc_provider_arn" {
  type = string
}

variable "namespace" {
  description = "Kubernetes namespace for the workers service account"
  type        = string
  default     = "deriv-dev"
}

variable "service_account_name" {
  description = "Kubernetes service account name for planner/executor"
  type        = string
  default     = "deriv-workers"
}

variable "invoke_policy_arn" {
  description = "IAM policy ARN from sagemaker-embedding module (InvokeEndpoint)"
  type        = string
}

variable "s3vectors_invoke_policy_arn" {
  description = "IAM policy ARN from s3vectors-index module (PutVectors/QueryVectors)"
  type        = string
  default     = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}
