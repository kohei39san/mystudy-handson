variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "commit_id" {
  type    = string
  default = "main"
}

variable "kube_version" {
  type    = string
  default = "v1.27.3"
}

variable "jmeter_version" {
  type    = string
  default = "5.6.2"
}
