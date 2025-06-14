terraform {
  required_version = ">= 1.0.0"
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.17.0"
    }
    kustomization = {
      source  = "kbst/kustomization"
      version = "0.9.6"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.6.2"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
  }
}

provider "kustomization" {
  kubeconfig_path = var.kubeconfig_path
}

provider "docker" {}
