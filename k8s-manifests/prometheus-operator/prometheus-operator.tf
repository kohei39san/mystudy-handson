data "http" "elastic_ip" {
  url = "https://ipinfo.io/ip"
}

locals {
  public_ip = "${data.http.elastic_ip.response_body}/32"
}

data "template_file" "values" {
  template = "${file("values/values.yaml")}"
  vars = {
    "public_ip" = "${local.public_ip}"
    "prometheus_nodeport" = "${var.prometheus_nodeport}"
    "grafana_nodeport" = "${var.grafana_nodeport}"
    "alertmanager_nodeport" = "${var.alertmanager_nodeport}"
  }
}

resource "helm_release" "kube-prometheus-stack" {
  name             = "kube-prometheus-stack"
  chart            = "https://github.com/prometheus-community/helm-charts/releases/download/kube-prometheus-stack-${var.prometheus_operator_version}/kube-prometheus-stack-${var.prometheus_operator_version}.tgz"
  namespace        = "monitoring"
  create_namespace = true
  values = [
    "${data.template_file.values.rendered}"
  ]
}
