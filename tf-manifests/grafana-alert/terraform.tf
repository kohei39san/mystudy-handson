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
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}
provider "http" {}

module "common_resources" {
  source = "../commons/simple-ec2-eice"
  vpc_security_group_ids = ["${resource.aws_security_group.prometheus_sg.id}"]
}
