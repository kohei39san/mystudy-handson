terraform {
  required_version = "~> 1.5.0"
  required_providers {
    aws = {
      source  = "registry.terraform.io/hashicorp/aws"
      version = "4.47.0"
    }
  }
}
