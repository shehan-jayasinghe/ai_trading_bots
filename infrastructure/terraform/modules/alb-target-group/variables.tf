variable "name" {
  description = "Target group name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "port" {
  description = "Target port (Jenkins 8080)"
  type        = number
  default     = 8080
}

variable "target_instance_id" {
  description = "Jenkins EC2 instance ID"
  type        = string
}

variable "tags" {
  description = "Tags applied to the target group"
  type        = map(string)
  default     = {}
}
