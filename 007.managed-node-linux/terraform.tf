terraform {
  required_version = "~> 1.9.6"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.98.0"
    }
    http = {
      source  = "hashicorp/http"
      version = "3.5.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}

provider "http" {}