terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.100.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.5.0"
    }
    null = {
      source  = "registry.terraform.io/hashicorp/null"
      version = "3.2.4"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}
