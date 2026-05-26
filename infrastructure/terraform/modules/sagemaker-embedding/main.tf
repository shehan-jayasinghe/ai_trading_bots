data "aws_partition" "current" {}

locals {
  # AWS Deep Learning Containers account (CPU Hugging Face inference) — us-west-1 and most commercial regions
  dlc_account_id = "763104351884"
  inference_image = coalesce(
    var.inference_image_uri,
    "${local.dlc_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/huggingface-pytorch-inference:2.1.1-transformers4.37.0-cpu-py310-ubuntu22.04-v1.0"
  )
  endpoint_name = "${var.name_prefix}-embed"
}

data "aws_iam_policy_document" "sagemaker_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["sagemaker.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "sagemaker" {
  name               = "${var.name_prefix}-sagemaker-embed"
  assume_role_policy = data.aws_iam_policy_document.sagemaker_assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "sagemaker" {
  role       = aws_iam_role.sagemaker.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_sagemaker_model" "embedding" {
  name               = "${var.name_prefix}-embed-model"
  execution_role_arn = aws_iam_role.sagemaker.arn

  primary_container {
    image = local.inference_image
    environment = {
      HF_MODEL_ID = var.hf_model_id
      HF_TASK     = "feature-extraction"
    }
  }

  tags = var.tags
}

resource "aws_sagemaker_endpoint_configuration" "embedding" {
  name = "${var.name_prefix}-embed-cfg"

  production_variants {
    variant_name = "AllTraffic"
    model_name   = aws_sagemaker_model.embedding.name

    serverless_config {
      memory_size_in_mb = var.serverless_memory_mb
      max_concurrency   = var.serverless_max_concurrency
    }
  }

  tags = var.tags
}

resource "aws_sagemaker_endpoint" "embedding" {
  name                 = local.endpoint_name
  endpoint_config_name = aws_sagemaker_endpoint_configuration.embedding.name
  tags                 = var.tags
}

data "aws_iam_policy_document" "invoke_endpoint" {
  statement {
    sid    = "InvokeEmbeddingEndpoint"
    effect = "Allow"
    actions = [
      "sagemaker:InvokeEndpoint",
    ]
    resources = [
      aws_sagemaker_endpoint.embedding.arn,
    ]
  }
}

resource "aws_iam_policy" "invoke_endpoint" {
  name   = "${var.name_prefix}-sagemaker-embed-invoke"
  policy = data.aws_iam_policy_document.invoke_endpoint.json
  tags   = var.tags
}
