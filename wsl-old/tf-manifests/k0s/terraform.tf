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

  required_version = ">= 1.11.0" # Set the minimum Terraform version
}
