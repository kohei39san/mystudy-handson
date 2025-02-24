module "nginx" {
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
      secret_generator = [{
        name = "nginx"
        type = "kubernetes.io/tls"
        files = [
          "kustomize/ssl/tls.crt",
          "kustomize/ssl/tls.key",
        ]
      }]
    }
  }
}
