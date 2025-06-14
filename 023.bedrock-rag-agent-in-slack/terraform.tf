terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    opensearch = {
      source  = "opensearch-project/opensearch"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Terraform   = "true"
    }
  }
}

provider "opensearch" {
  url                 = module.main_stack.opensearch_endpoint != "" ? "https://${module.main_stack.opensearch_endpoint}" : ""
  aws_region          = var.aws_region
  aws_assume_role_arn = module.main_stack.bedrock_opensearch_role_arn
  insecure            = true
  opensearch_version  = "2"
}