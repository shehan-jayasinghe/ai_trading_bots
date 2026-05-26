# S3 Vectors bucket (Terraform only)

Creates a single **Amazon S3 Vectors** vector bucket via the **awscc** provider
(`awscc_s3vectors_vector_bucket`). This is not a regular S3 object bucket.

Uses **awscc** so the rest of dev can stay on **hashicorp/aws** ~> 5.x (EKS module constraint).

Indexes and worker IAM are added in a later change.
