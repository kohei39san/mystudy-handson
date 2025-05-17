# tflint-ignore: terraform_required_version
terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.98.0"
    }
    null = {
      source  = "registry.terraform.io/hashicorp/null"
      version = "3.2.4"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.5.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}
