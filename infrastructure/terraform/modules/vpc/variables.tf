variable "name" {
  description = "VPC name prefix"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
}

variable "single_nat_gateway" {
  description = "Use a single NAT gateway (cheaper for dev)"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags applied to VPC resources"
  type        = map(string)
  default     = {}
}
