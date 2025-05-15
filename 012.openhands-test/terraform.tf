terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.98.0" # Latest version as of 2025-04-26
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
}
