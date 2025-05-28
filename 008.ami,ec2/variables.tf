variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "ami" {
  type    = string
  default = "ami-01a4140d4968cb175"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "iam_role_name" {
  type    = string
  default = "ami_ec2_managed_node_role"
}

variable "iam_instance_profile" {
  type    = string
  default = "managed_node_instance_profile"
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
  default = "managed_node_linux_key_pair"
}

variable "lambda_cfnstack_name" {
  type    = string
  default = "ManaagedNodeLinuxLambda"
}

variable "lambda_function_name" {
  type    = string
  default = "lambda-ami-ec2"
}
variable "key_pair_public" {
  type    = string
  default = ""
}

variable "key_pair_private" {
  type    = string
  default = ""
}

variable "ami_name" {
  type    = string
  default = ""
}