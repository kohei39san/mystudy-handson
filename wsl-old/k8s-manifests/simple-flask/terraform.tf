terraform {
  required_providers {
    kustomization = {
      source  = "kbst/kustomization"
      version = ">= 0.9.4"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.10.1"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 3.0.2"
    }
    #    http = {
    #      source = "hashicorp/http"
    #      version = ">= 3.4.0"
    #    }
  }

  required_version = ">= 1.11.7"
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
