variable "loki_s3_lifecycle_expire_days" {
  description = "S3 lifecycle expiration for Loki log chunks (days)"
  type        = number
  default     = 90
}
