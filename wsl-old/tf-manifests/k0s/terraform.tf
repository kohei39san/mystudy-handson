terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "6.46.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.6.0"
    }
    null = {
      source  = "registry.terraform.io/hashicorp/null"
      version = "3.3.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}
provider "http" {}
provider "null" {}

module "common_resources" {
  source = "../commons/simple-ec2"
}
