resource "null_resource" "build_nginx_ingress_controller_image" {
  provisioner "local-exec" {
    command = "cd kustomize/kubernetes-ingress && make debian-image TARGET=container"
  }
  provisioner "local-exec" {
    command = "minikube image load nginx/nginx-ingress:$(docker images | grep nginx-ingress | awk '{print $2}')"
  }
}

module "ingress_controller" {
  source  = "kbst.xyz/catalog/custom-manifests/kustomization"
  version = "0.4.0"

  configuration_base_key = "default"

  configuration = {
    default = {
      namespace = "nginx-ingress"
      resources = [
        "kustomize/kubernetes-ingress/deployments/common/ns-and-sa.yaml",
        "kustomize/kubernetes-ingress/deployments/rbac/rbac.yaml",
        "kustomize/kubernetes-ingress/deployments/rbac/apdos-rbac.yaml",
        "kustomize/kubernetes-ingress/examples/shared-examples/default-server-secret/default-server-secret.yaml",
        "kustomize/kubernetes-ingress/deployments/common/nginx-config.yaml",
        "kustomize/kubernetes-ingress/deployments/common/ingress-class.yaml",
        "kustomize/kubernetes-ingress/deployments/common/crds/k8s.nginx.org_virtualservers.yaml",
        "kustomize/kubernetes-ingress/deployments/common/crds/k8s.nginx.org_virtualserverroutes.yaml",
        "kustomize/kubernetes-ingress/deployments/common/crds/k8s.nginx.org_transportservers.yaml",
        "kustomize/kubernetes-ingress/deployments/common/crds/k8s.nginx.org_policies.yaml",
        "kustomize/kubernetes-ingress/deployments/deployment/nginx-ingress.yaml",
        "kustomize/kubernetes-ingress/deployments/service/nodeport.yaml",
      ]
    }
  }
  depends_on = ["null_resource.build_nginx_ingress_controller_image"]
}
