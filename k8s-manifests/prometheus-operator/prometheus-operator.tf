data "http" "elastic_ip" {
  url = "http://169.254.169.254/latest/meta-data/public-ipv4"
}

locals {
  public_ip = replace("${data.http.elastic_ip.response_body}/32", "\n", "")
}

resource "helm_release" "kube-prometheus-stack" {
  name             = "kube-prometheus-stack"
  chart            = "https://github.com/prometheus-community/helm-charts/releases/download/kube-prometheus-stack-${var.prometheus_operator_version}/kube-prometheus-stack-${var.prometheus_operator_version}.tgz"
  namespace        = "monitoring"
  create_namespace = true
  values = [
    "${file("values/values.yaml")}"
  ]
}
