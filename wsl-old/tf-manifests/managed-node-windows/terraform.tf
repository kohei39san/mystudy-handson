terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = ">=5.59.0" # Use >= to specify minimum version for compatibility
    }
    http = {
      source  = "hashicorp/http"
      version = "3.4.3"
    }
  }

  required_version = ">=1.11.4, <2.0.0" # Specify the range of compatible versions
}

provider "aws" {
  default_tags {
    tags = var.aws_tags
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
