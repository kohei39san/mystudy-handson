terraform {
  required_version = ">= 1.9.6"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 8.10"
    }
  }

  backend "oci" {}
}

provider "oci" {
  region = var.region
}