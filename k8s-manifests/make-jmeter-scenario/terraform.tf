terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.10.1"
    }
    kustomization = {
      source  = "kbst/kustomization"
      version = "0.9.4"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path = "${var.kubeconfig_path}"
  }
}

provider "kustomization" {
  kubeconfig_path = "${var.kubeconfig_path}"
}

provider "docker" {}
