variable "aws_tags" {
  type = map(string)
  default = {
    Environment = "dev"
    Terraform   = "true"
  }
}

variable "ami" {
  type    = string
  default = "" # Will use the data source for the latest Windows AMI
}

variable "instance_type" {
  type    = string
  default = "t2.medium"
}

variable "iam_role_name" {
  type    = string
  default = "windows_managed_instance_managed_node_role"
}

variable "iam_instance_profile" {
  type    = string
  default = "windows_managed_instance_profile"
}

variable "root_block_volume_size" {
  type    = number
  default = 50
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
  default = "windows_managed_instance_key_pair"
}

variable "key_pair_public" {
  type    = string
  default = ""
}

variable "key_pair_private" {
  type    = string
  default = ""
}