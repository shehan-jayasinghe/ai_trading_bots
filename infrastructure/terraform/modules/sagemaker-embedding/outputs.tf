output "endpoint_name" {
  description = "SageMaker real-time/serverless endpoint name for embedding invocations"
  value       = aws_sagemaker_endpoint.embedding.name
}

output "endpoint_arn" {
  description = "SageMaker endpoint ARN"
  value       = aws_sagemaker_endpoint.embedding.arn
}

output "model_name" {
  description = "SageMaker model resource name"
  value       = aws_sagemaker_model.embedding.name
}

output "hf_model_id" {
  description = "Hugging Face model ID loaded by the endpoint"
  value       = var.hf_model_id
}

output "invoke_policy_arn" {
  description = "IAM policy ARN granting sagemaker:InvokeEndpoint on this endpoint"
  value       = aws_iam_policy.invoke_endpoint.arn
}

output "sagemaker_execution_role_arn" {
  description = "SageMaker execution role ARN"
  value       = aws_iam_role.sagemaker.arn
}
