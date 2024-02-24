variable "instance_id" {
  type    = string
  default = "instance id"
}

variable "public_ip" {
  type    = string
  default = ""
}

variable "ssh_user" {
  type    = string
  default = "ec2-user"
}

variable "ssh_private_key" {
  type    = string
  default = "private key"
}

variable "ssh_public_key" {
  type    = string
  default = "public key"
}

variable "scripts" {
  type    = list(string)
  default = []
}

variable "inline" {
  type = list(string)
  default = []
}

variable "environment" {
  type = map(string)
  default = {}
}
