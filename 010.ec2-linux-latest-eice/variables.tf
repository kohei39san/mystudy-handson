variable "ami_name" {
  type    = string
  default = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64"
}

variable "aws_tags" {
  type = map(string)
  default = {
    Environment = "dev"
    Terraform   = "true"
  }
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
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

variable "sg_eice_name" {
  type    = string
  default = "sg_eice"
}

variable "key_pair_public" {
  type    = string
  default = ""
}

variable "key_pair_private" {
  type    = string
  default = ""
}