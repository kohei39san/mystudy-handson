resource "null_resource" "build_nginx_ingress_controller_image" {
  provisioner "local-exec" {
    command = "cd kustomize/kubernetes-ingress && make debian-image TARGET=container"
  }
  provisioner "local-exec" {
    command = "minikube image load nginx/nginx-ingress:$(docker images | grep nginx-ingress | awk '{print $2}')"
  }
}

data "kustomization_overlay" "ingress_controller" {
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
  patches {
    patch = <<-EOF
      - op: add
        path: /spec/template/spec/containers/0/args/-
        value: -enable-snippets
    EOF
    target {
      group   = "apps"
      version = "v1"
      kind    = "Deployment"
      name    = "nginx-ingress"
    }
  }
}

resource "kustomization_resource" "ingress_controller" {
  for_each = data.kustomization_overlay.ingress_controller.ids
  manifest = data.kustomization_overlay.ingress_controller.manifests[each.value]
}
