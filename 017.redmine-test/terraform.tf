terraform {
  required_version = "~> 1.11.4"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "~> 4.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.4.5"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project = "Redmine"
      Environment = "Test"
    }
  }
}

provider "http" {}