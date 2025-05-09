variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "ami_name" {
  type    = string
  default = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64"
}

variable "instance_type" {
  type    = string
  default = "t2.xlarge"
}

variable "iam_instance_profile" {
  type    = string
  default = ""
}

variable "root_block_volume_size" {
  type    = number
  default = 50
}

variable "key_name" {
  type    = string
  default = "key_server"
}

variable "instance_public_key" {
  type    = string
  default = ""
}

variable "instance_private_key" {
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

variable "sg_name" {
  type    = string
  default = "sg_server"
}