terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.59.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}

module "common_resources" {
  source               = "../commons/simple-ec2-eice"
  iam_instance_profile = aws_iam_instance_profile.managed_node_instance_profile.id
  instance_type        = var.instance_type
}
