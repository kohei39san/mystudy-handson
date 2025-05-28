variable "aws_tags" {
  type = map(string)
  default = {
    Environment = "dev"
    Terraform   = "true"
  }
}

variable "ami" {
  type    = string
  default = "ami-01a4140d4968cb175"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "iam_instance_profile" {
  type    = string
  default = "managed_node_linux_instance_profile"
}

variable "root_block_volume_size" {
  type    = number
  default = 8
}

variable "vpc_cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "subnet_cidr_block" {
  type    = string
  default = "10.0.0.0/24"
}

variable "key_pair" {
  type    = string
  default = "manaaged_node_linux_key_pair"
}

variable "key_pair_public" {
  type    = string
  default = ""
}

variable "key_pair_private" {
  type    = string
  default = ""
}