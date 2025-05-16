terraform {
  required_version = ">= 1.11.4, < 2.0.0"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "~> 5.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.5.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = var.tags
  }
}

provider "http" {}