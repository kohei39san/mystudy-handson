terraform {
  required_version = "~> 1.9.6"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.67.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.4.5"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project = "Redmine"
      Environment = "Test"
    }
  }
}

provider "http" {}