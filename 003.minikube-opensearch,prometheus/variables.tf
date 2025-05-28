variable "aws_tags" {
  type = map(string)
  default = {
    Environment = "dev"
    Terraform   = "true"
  }
}

variable "ami_name" {
  type    = string
  default = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64"
}

variable "instance_type" {
  type    = string
  default = "t2.xlarge"
}

variable "iam_instance_profile" {
  type        = string
  description = "IAM instance profile for the EC2 instance"
  default     = "minikube-instance-profile"
}

variable "root_block_volume_size" {
  type    = number
  default = 50
}

# Removed unused variable key_name

variable "instance_public_key" {
  type    = string
  default = ""
}

variable "instance_private_key" {
  type    = string
  default = ""
}

variable "vpc_cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "subnet_cidr_block" {
  type    = string
  default = "10.0.0.0/24"
}

variable "sg_name" {
  type    = string
  default = "sg_server"
}

variable "environment" {
  type        = string
  description = "Environment name for tagging resources"
  default     = "dev"
}