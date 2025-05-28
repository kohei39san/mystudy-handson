terraform {
  required_version = ">= 1.0.0"
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
    tags = merge(var.aws_tags, {
      Environment = "Development"
      Terraform   = "true"
    })
  }
}

provider "http" {}

module "common" {
  source                 = "../commons/simple-ec2"
  ami_name               = var.ami_name
  iam_instance_profile   = aws_iam_instance_profile.managed_node_instance_profile.id
  instance_type          = var.instance_type
  root_block_volume_size = var.root_block_volume_size
  vpc_security_group_ids = [aws_security_group.sg.id]
  key_pair               = var.key_pair
}
