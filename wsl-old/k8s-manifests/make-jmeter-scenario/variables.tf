variable "kubeconfig_path" {
  type    = string
  default = "~/.kube/config"
}

variable "nginx_lb_image_tag" {
  type    = string
  default = "nginx-lb:v1.0"
}
