module "nginx1" {
  source  = "kbst.xyz/catalog/custom-manifests/kustomization"
  version = "0.4.0"

  configuration_base_key = "default"

  configuration = {
    default = {
      namespace = "default"
      resources = [
        "kustomize/nginx.yaml",
        "kustomize/ingress.yaml",
      ]
    }
  }
}
