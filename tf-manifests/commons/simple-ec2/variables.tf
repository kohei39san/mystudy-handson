variable "ami_name" {
  type    = string
  default = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
}

variable "instance_type" {
  type    = string
  default = "t2.medium"
}

variable "iam_instance_profile" {
  type    = string
  default = ""
}

variable "root_block_volume_size" {
  type    = number
  default = 20
}

variable "instance_public_key" {
  type    = string
  default = "public-key-path"
}

variable "instance_private_key" {
  type    = string
  default = "private-key-path"
}

variable "vpc_security_group_ids" {
  type    = list(string)
  default = []
}
