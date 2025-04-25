terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = ">= '5.19.0'"
    }
  }

  required_version = ">= '1.11.4'"

  provider "aws" {
    default_tags {
      tags = var.aws_tags
    }
  }
}
