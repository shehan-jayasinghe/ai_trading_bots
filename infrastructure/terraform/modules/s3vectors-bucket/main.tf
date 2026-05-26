resource "awscc_s3vectors_vector_bucket" "this" {
  vector_bucket_name = var.vector_bucket_name

  encryption_configuration = {
    sse_type = "AES256"
  }

  tags = [
    for k, v in var.tags : {
      key   = k
      value = v
    }
  ]
}
