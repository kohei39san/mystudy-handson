# Terraform and Provider Version Constraints

terraform {
  required_version = ">= 1.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }

    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }

    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
    }
  }
}