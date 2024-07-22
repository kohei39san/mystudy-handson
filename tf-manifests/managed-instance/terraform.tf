terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.59.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.4.3"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}
provider "http" {}

module "common_resources" {
  source = "../commons/simple-ec2"
}
