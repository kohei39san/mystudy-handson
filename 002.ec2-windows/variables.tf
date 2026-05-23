variable "instance_type" {
  type    = string
  default = "t2.medium"
}

variable "root_block_volume_size" {
  type    = number
  default = 30
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
  type    = map(string)
  default = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging resources"
  default     = "dev"
}

variable "ami_id" {
  type        = string
  description = "AMI ID for the Windows instance"
  default     = ""
}