resource "helm_release" "nginx-ingress" {
  name             = "nginx-ingress"
  chart            = "oci://ghcr.io/nginxinc/charts/nginx-ingress"
  namespace        = "nginx-ingress"
  create_namespace = true
  values = [
    "${file("kustomize/nginx-ingress/values.yaml")}"
  ]
}
