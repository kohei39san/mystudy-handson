data "http" "metadata_token" {
  url    = "http://169.254.169.254/latest/api/token"
  method = "PUT"
  request_headers = {
    "X-aws-ec2-metadata-token-ttl-seconds" = "21600"
  }
}

data "http" "elastic_ip" {
  url = "http://169.254.169.254/latest/meta-data/public-ipv4"
  request_headers = {
    "X-aws-ec2-metadata-token" = ""
  }
}

locals {
  token = "${data.http.metadata_token.response_body}"
  public_ip = replace("${data.http.elastic_ip.response_body}/32", "\n", "")
}

data "template_file" "values" {
  template = "${file("values/values.yaml")}"
  vars = {
    public_ip = "${local.token}"
    prometheus_nodeport = "${var.prometheus_nodeport}"
    grafana_nodeport = "${var.grafana_nodeport}"
    alertmanager_nodeport = "${var.alertmanager_nodeport}"
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
