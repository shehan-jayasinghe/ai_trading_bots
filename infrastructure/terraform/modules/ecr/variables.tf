variable "repository_names" {
  description = "ECR repository names to create"
  type        = list(string)
}

variable "tags" {
  description = "Tags applied to ECR repositories"
  type        = map(string)
  default     = {}
}
