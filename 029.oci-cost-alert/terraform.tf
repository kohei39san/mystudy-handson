terraform {
  required_version = ">= 1.9.6"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 7.0"
    }
  }
  
  backend "oci" {
    # Required
    bucket            = "terraform_state_bucket"
    config_file_profile = "DEFAULT"
  }
}

provider "oci" {
  region = var.region
}