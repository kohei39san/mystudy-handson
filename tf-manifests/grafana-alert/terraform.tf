terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.38.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.4.1"
    }
    null = {
      source  = "registry.terraform.io/hashicorp/null"
      version = "3.2.2"
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
  source = "../commons/simple-ec2-eice"
}
