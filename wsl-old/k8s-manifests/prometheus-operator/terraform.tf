# tflint-ignore: terraform_required_version
terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.17.0"
    }
    http = {
      source  = "registry.terraform.io/hashicorp/http"
      version = "3.5.0"
    }
    template = {
      source  = "hashicorp/template"
      version = "2.2.0"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}
provider "http" {}
provider "template" {}
