resource "helm_release" "kube-prometheus-stack" {
  name = "kube-prometheus-stack"
  chart = "https://github.com/prometheus-community/helm-charts/releases/download/kube-prometheus-stack-47.0.0/kube-prometheus-stack-47.0.0.tgz"
  namespace  = "monitoring"
  create_namespace = true
  values = [
    "${file("kustomize/prometheus-operator/values.yaml")}"
  ]
}
