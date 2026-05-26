resource "awscc_s3vectors_index" "this" {
  index_name         = var.index_name
  vector_bucket_name = var.vector_bucket_name
  data_type          = "float32"
  dimension          = var.dimension
  distance_metric    = var.distance_metric

  tags = [
    for k, v in var.tags : {
      key   = k
      value = v
    }
  ]
}

data "aws_iam_policy_document" "invoke" {
  statement {
    sid    = "S3VectorsQueryPut"
    effect = "Allow"
    actions = [
      "s3vectors:PutVectors",
      "s3vectors:QueryVectors",
      "s3vectors:GetVectors",
      "s3vectors:DeleteVectors",
      "s3vectors:GetIndex",
      "s3vectors:ListVectors",
    ]
    resources = [
      awscc_s3vectors_index.this.index_arn,
      "arn:aws:s3vectors:*:*:bucket/${var.vector_bucket_name}",
      "arn:aws:s3vectors:*:*:bucket/${var.vector_bucket_name}/index/${var.index_name}",
    ]
  }
}

resource "aws_iam_policy" "invoke" {
  name   = "${var.vector_bucket_name}-${var.index_name}-invoke"
  policy = data.aws_iam_policy_document.invoke.json
  tags   = var.tags
}
