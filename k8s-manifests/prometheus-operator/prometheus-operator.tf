resource "helm_release" "kube-prometheus-stack" {
  name             = "kube-prometheus-stack"
  chart            = "https://github.com/prometheus-community/helm-charts/releases/download/kube-prometheus-stack-${var.prometheus_operator_version}/kube-prometheus-stack-${var.prometheus_operator_version}.tgz"
  namespace        = "monitoring"
  create_namespace = true
  values = [
    "${file("values/values.yaml")}"
  ]
}
