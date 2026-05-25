output "bucket_id" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.loki.id
}

output "bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.loki.arn
}
