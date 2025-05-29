variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "iam_instance_profile_name" {
  type    = string
  default = "managed_node_instance_profile"
}
