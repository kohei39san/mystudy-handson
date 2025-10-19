terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  backend "oci" {}
}

provider "aws" {
  region = "ap-northeast-1"

  default_tags {
    tags = {
      Project     = "apigateway-cognito-lambda-payload"
      Environment = var.environment
      ManagedBy   = "terraform"
      Terraform   = "true"
    }
  }
}