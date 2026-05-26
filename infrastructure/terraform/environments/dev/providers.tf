terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    awscc = {
      source  = "hashicorp/awscc"
      version = ">= 1.79.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  shared_credentials_files = [pathexpand("${path.module}/.aws/credentials")]

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

provider "awscc" {
  region = var.aws_region

  shared_credentials_files = [pathexpand("${path.module}/.aws/credentials")]
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
  }

  eks_cluster_name = "${var.project_name}-${var.environment}"

  s3vectors_bucket_name = "${var.project_name}-${var.environment}-rag-vectors"
}

data "aws_route53_zone" "root" {
  name         = var.root_domain
  private_zone = false
}
