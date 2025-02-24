variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "ami_name" {
  type    = string
  default = "/aws/service/ami-windows-latest/Windows_Server-2022-English-Full-Base"
}

variable "root_block_volume_size" {
  type    = number
  default = 30
}

variable "key_pair" {
  type    = string
  default = "manaaged_node_windows_key_pair"
}

variable "key_pair_public" {
  type    = string
  default = ""
}

variable "key_pair_private" {
  type    = string
  default = ""
}

variable "sg_name" {
  type    = string
  default = "managed_node_windows_security_group"
}

variable "rdp_port" {
  type    = number
  default = 3389
}
