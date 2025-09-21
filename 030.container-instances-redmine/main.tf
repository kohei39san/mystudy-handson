# OCI Provider Configuration
terraform {
  backend "oci" {}
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 7.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
  required_version = ">= 1.0"
}

provider "oci" {
  region = var.region
}

provider "docker" {
  registry_auth {
    address  = "${var.region}.ocir.io"
    username = var.docker_registry_username
    password = oci_identity_auth_token.auth_token.token
  }
}

# Data sources
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}