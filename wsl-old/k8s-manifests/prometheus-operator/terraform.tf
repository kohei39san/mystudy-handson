terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.12.1"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.4.1"
    }
    template = {
      source  = "hashicorp/template"
      version = "2.2.0"
    }
  }

  required_version = ">= v1.11.4"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}
provider "http" {}
provider "template" {}
