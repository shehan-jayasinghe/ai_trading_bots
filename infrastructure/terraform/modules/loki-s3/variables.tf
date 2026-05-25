variable "bucket_name" {
  description = "Globally unique S3 bucket name for Loki chunk storage"
  type        = string
}

variable "lifecycle_expire_days" {
  description = "Delete objects after N days (long-term archive for AI phase; adjust per env)"
  type        = number
  default     = 90
}

variable "tags" {
  description = "Tags applied to the bucket"
  type        = map(string)
  default     = {}
}
