terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.98.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = {
      Environment = "Development"
      Terraform   = "true"
    }
  }
}

