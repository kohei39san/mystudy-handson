variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "ami" {
  type    = string
  default = "/aws/service/ami-windows-latest/Windows_Server-2016-Japanese-Full-Base"
}

variable "instance_type" {
  type    = string
  default = "t2.medium"
}

variable "iam_instance_profile" {
  type    = string
  default = "managed_node_instance_profile"
}

variable "root_block_volume_size" {
  type    = number
  default = 50
}

variable "ami_name" {
  type    = string
  default = ""
}

variable "vpc_cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "subnet_cidr_block" {
  type    = string
  default = "10.0.0.0/24"
}

variable "rdp_port" {
  type    = number
  default = 3389
}

variable "key_pair" {
  type    = string
  default = "managed-node-windows-key-pair"
}

variable "key_pair_public" {
  type    = string
  default = ""
}

variable "key_pair_private" {
  type    = string
  default = ""
}