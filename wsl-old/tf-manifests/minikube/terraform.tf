terraform {
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "4.47.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.2.1"
    }
    null = {
      source  = "registry.terraform.io/hashicorp/null"
      version = "3.2.1"
    }
  }

  required_version = ">= v1.11.0"
}
