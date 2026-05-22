variable "name" {
  description = "Name prefix for Jenkins EC2 resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Public subnet ID for Jenkins EC2"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for Jenkins EC2 (us-west-1 Ubuntu)"
  type        = string
}

variable "public_key" {
  description = "SSH public key material (creates aws_key_pair in AWS)"
  type        = string
}

variable "security_group_ids" {
  description = "Security group IDs attached to Jenkins EC2"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "volume_size_gb" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 40
}

variable "eks_cluster_arn" {
  description = "EKS cluster ARN for Jenkins CI (kubectl / deploy pipelines)"
  type        = string
}

variable "tags" {
  description = "Tags applied to Jenkins resources"
  type        = map(string)
  default     = {}
}
