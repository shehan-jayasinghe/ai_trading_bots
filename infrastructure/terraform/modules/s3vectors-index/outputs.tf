output "index_name" {
  value = awscc_s3vectors_index.this.index_name
}

output "index_arn" {
  value = awscc_s3vectors_index.this.index_arn
}

output "invoke_policy_arn" {
  description = "IAM policy for workers to PutVectors/QueryVectors on this index"
  value       = aws_iam_policy.invoke.arn
}
