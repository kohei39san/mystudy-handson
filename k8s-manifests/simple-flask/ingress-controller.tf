module "ingress_controller" {
  source  = "kbst.xyz/catalog/custom-manifests/kustomization"
  version = "0.4.0"

  configuration_base_key = "default"

  configuration = {
    default = {
      namespace = "nginx-ingress"
      resources = [
        "../../container-images/kubernetes-ingress/deployments/common/ns-and-sa.yaml",
        "../../container-images/kubernetes-ingress/deployments/rbac/rbac.yaml",
        "../../container-images/kubernetes-ingress/deployments/rbac/apdos-rbac.yaml",
        "../../container-images/kubernetes-ingress/deployments/common/default-server-secret.yaml",
        "../../container-images/kubernetes-ingress/deployments/common/nginx-config.yaml",
        "../../container-images/kubernetes-ingress/deployments/common/ingress-class.yaml",
        "../../container-images/kubernetes-ingress/deployments/common/crds/k8s.nginx.org_virtualservers.yaml",
        "../../container-images/kubernetes-ingress/deployments/common/crds/k8s.nginx.org_virtualserverroutes.yaml",
        "../../container-images/kubernetes-ingress/deployments/common/crds/k8s.nginx.org_transportservers.yaml",
        "../../container-images/kubernetes-ingress/deployments/common/crds/k8s.nginx.org_policies.yaml",
        "../../container-images/kubernetes-ingress/deployments/deployment/nginx-ingress.yaml",
        "../../container-images/kubernetes-ingress/deployments/service/nodeport.yaml",
      ]
    }
  }

}
