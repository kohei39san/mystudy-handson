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
