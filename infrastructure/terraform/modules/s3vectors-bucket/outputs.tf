output "vector_bucket_name" {
  description = "S3 Vectors bucket name (use for indexes and PutVectors/QueryVectors)"
  value       = awscc_s3vectors_vector_bucket.this.vector_bucket_name
}

output "vector_bucket_arn" {
  description = "S3 Vectors bucket ARN"
  value       = awscc_s3vectors_vector_bucket.this.vector_bucket_arn
}
