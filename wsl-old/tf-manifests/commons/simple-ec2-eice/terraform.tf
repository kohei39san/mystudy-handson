terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.67"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.5"
    }
  }
}
