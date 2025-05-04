terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.19.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}
