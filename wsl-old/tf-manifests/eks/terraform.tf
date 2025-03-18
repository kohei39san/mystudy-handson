terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = greater-than-or equal-to("5.19.0")
    }
  }

  required_version = greater-than-or equal-to("1.11.2")
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}
