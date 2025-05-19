terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.98.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7.0"
    }
    opensearch = {
      source  = "opensearch-project/opensearch"
      version = "~> 2.3.0"
    }
  }
}

provider "opensearch" {
  url                 = aws_opensearch_domain.vector_store.endpoint
  aws_region          = var.aws_region
  sign_aws_requests   = true
  aws_assume_role_arn = aws_iam_role.bedrock_opensearch.arn
  insecure            = false
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.default_tags
  }
}
