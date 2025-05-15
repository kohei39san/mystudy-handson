terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "4.47.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.2.1"
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
provider "http" {}
provider "null" {}

module "common_resources" {
  source = "../commons/simple-ec2"
}
