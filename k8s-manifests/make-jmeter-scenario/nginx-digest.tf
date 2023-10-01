module "nginx-digest" {
  source  = "kbst.xyz/catalog/custom-manifests/kustomization"
  version = "0.4.0"

  configuration_base_key = "default"

  configuration = {
    default = {
      namespace = "default"
      resources = [
        "kustomize/nginx-digest.yaml",
      ]
      secret_generator = [
        {
          name = "nginx-digest"
          type = "Opaque"
          files = [
            "kustomize/digest/.htdigest",
          ]
        },
        {
          name = "nginx-tls"
          type = "kubernetes.io/tls"
          files = [
            "kustomize/ssl/tls.crt",
            "kustomize/ssl/tls.key",
          ]
        }
      ]
    }
  }
}
