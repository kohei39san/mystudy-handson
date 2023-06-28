module "postgres_operator" {
  source  = "kbst.xyz/catalog/custom-manifests/kustomization"
  version = "0.4.0"

  configuration_base_key = "default"

  configuration = {
    default = {
      namespace = "postgresql"
      resources = [
        "https://raw.githubusercontent.com/zalando/postgres-operator/master/manifests/configmap.yaml",
        "https://raw.githubusercontent.com/zalando/postgres-operator/master/manifests/operator-service-account-rbac.yaml",
        "https://raw.githubusercontent.com/zalando/postgres-operator/master/manifests/postgres-operator.yaml",
        "https://raw.githubusercontent.com/zalando/postgres-operator/master/manifests/api-service.yaml",
        "kustomize/postgres-cluster.yaml",
        "kustomize/pgpool.yaml",
      ]
    }
  }
}
