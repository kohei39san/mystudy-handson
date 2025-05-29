terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.98.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = {
      Environment = "Development"
      Terraform   = "true"
    }
  }
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
  }
}

module "common_resources" {
  source               = "../commons/ec2-eice-tunnel"
  iam_instance_profile = aws_iam_instance_profile.managed_node_instance_profile.id
  instance_type        = var.instance_type
}
