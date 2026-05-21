variable "name" {
  description = "ALB name"
  type        = string
}

variable "security_group_ids" {
  description = "Security groups for the ALB"
  type        = list(string)
}

variable "subnet_ids" {
  description = "Public subnet IDs for the ALB"
  type        = list(string)
}

variable "target_group_arn" {
  description = "Default target group ARN"
  type        = string
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS listener"
  type        = string
}

variable "tags" {
  description = "Tags applied to the ALB"
  type        = map(string)
  default     = {}
}
