terraform {
  required_version = ">= 1.9.6"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.100.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}