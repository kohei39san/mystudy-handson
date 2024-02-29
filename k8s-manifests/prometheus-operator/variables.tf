variable "prometheus_operator_version" {
  type    = string
  default = "56.16.0"
}

variable "grafana_nodeport" {
  type = number
  default = 30100
}

variable "prometheus_nodeport" {
  type = number
  default = 30200
}

variable "alertmanager_nodeport" {
  type = number
  default = 30300
}
