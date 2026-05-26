variable "vector_bucket_name" {
  description = "Name of the Amazon S3 Vectors vector bucket (not a standard S3 bucket)"
  type        = string
}

variable "tags" {
  description = "Tags for the vector bucket"
  type        = map(string)
  default     = {}
}
