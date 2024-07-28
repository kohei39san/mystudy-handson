variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "bucket_name" {
  type    = string
  default = "managed-node-s3"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "ami_name" {
  type = string
  default = "/aws/service/ami-windows-latest/Windows_Server-2022-English-Core-Base"
}

variable "root_block_volume_size" {
  type = number
  default = 30
}
