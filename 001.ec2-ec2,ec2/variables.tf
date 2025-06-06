variable "ami_name" {
  type    = string
  default = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "root_block_volume_size" {
  type    = number
  default = 8
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

variable "aws_tags" {
  type = map(string)
  default = {
    Environment = "dev"
    Terraform   = "true"
  }
}

variable "environment" {
  type        = string
  description = "Environment name for tagging resources"
  default     = "dev"
}