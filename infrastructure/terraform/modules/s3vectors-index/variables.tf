variable "vector_bucket_name" {
  description = "S3 Vectors bucket name (must exist)"
  type        = string
}

variable "index_name" {
  description = "Vector index name inside the bucket"
  type        = string
  default     = "trade-embeddings"
}

variable "dimension" {
  description = "Embedding dimension (all-MiniLM-L6-v2 = 384)"
  type        = number
  default     = 384
}

variable "distance_metric" {
  description = "Similarity metric: cosine or euclidean"
  type        = string
  default     = "cosine"
}

variable "tags" {
  type    = map(string)
  default = {}
}
