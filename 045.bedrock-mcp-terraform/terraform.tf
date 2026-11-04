terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.0, < 7.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.tags
  }
}

data "aws_ecr_authorization_token" "agent" {}

provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.agent.proxy_endpoint
    username = data.aws_ecr_authorization_token.agent.user_name
    password = data.aws_ecr_authorization_token.agent.password
  }
}

