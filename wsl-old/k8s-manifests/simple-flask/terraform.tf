terraform {
  required_version = ">= 1.0.0"
  required_providers {
    kustomization = {
      source  = "kbst/kustomization"
      version = "0.9.6"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.17.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.6.1"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    #    http = {
    #      source = "hashicorp/http"
    #      version = "3.4.0"
    #    }
  }
}

provider "kustomization" {
  kubeconfig_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

provider "docker" {}

#provider "http" {}
