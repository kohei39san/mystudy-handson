terraform {
  required_version = ">= 1.9.6"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "5.99.1"
    }
    http = {
      source  = "hashicorp/http"
      version = "3.5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
  default_tags {
    tags = merge(var.aws_tags, {
      Environment = "Development"
      Terraform   = "true"
    })
  }
}

provider "aws" {
  region = "ap-northeast-3"
  alias  = "osaka"
  default_tags {
    tags = var.aws_tags
  }
}

provider "http" {}