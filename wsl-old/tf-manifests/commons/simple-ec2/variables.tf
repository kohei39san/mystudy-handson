variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "ami_name" {
  type    = string
  default = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "iam_instance_profile" {
  type        = string
  default     = "simple_ec2_instance_profile"
  description = "IAM instance profile for EC2 instance"
}

variable "root_block_volume_size" {
  type    = number
  default = 20
}

variable "vpc_security_group_ids" {
  type    = list(string)
  default = []
}

variable "key_pair" {
  type        = string
  default     = "simple_ec2_key"
  description = "SSH key name for EC2 instance"
}

variable "vpc_cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "subnet_cidr_block" {
  type    = string
  default = "10.0.0.0/24"
}
