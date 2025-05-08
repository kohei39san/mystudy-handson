provider "aws" {
  region = var.region
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.0.0"
}

# Key pair for SSH access
resource "aws_key_pair" "redmine_key" {
  key_name   = "redmine-key"
  public_key = file(var.public_key_path)
}