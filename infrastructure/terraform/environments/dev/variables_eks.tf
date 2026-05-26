variable "eks_cluster_version" {
  description = "Kubernetes version for EKS control plane (must be supported in region; upgrade one minor at a time from existing cluster)"
  type        = string
  default     = "1.31"
}

variable "eks_node_instance_types" {
  type    = list(string)
  default = ["t2.medium"]
}

variable "eks_node_desired_size" {
  description = "EKS managed node group desired capacity (dev uses 5 for platform + monitoring pod headroom)"
  type        = number
  default     = 5
}

variable "eks_node_min_size" {
  description = "0 allows park-platform to scale nodes to zero without terraform destroy"
  type        = number
  default     = 0
}

variable "eks_node_max_size" {
  type    = number
  default = 5
}
