#
# aws
#

variable "aws_tags" {
  type = map(string)
  default = {
    Environment = "dev"
    Terraform   = "true"
  }
}

variable "vpc_cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "num_subnets" {
  type    = number
  default = "2"
}

#
# EKS
#

variable "cluster_name" {
  type    = string
  default = "eks-study"
}

variable "cluster_version" {
  type    = string
  default = "1.27"
}

variable "node_group_name" {
  type    = string
  default = "node_group"
}

variable "node_instance_types" {
  type    = list(string)
  default = ["t2.micro"]
}

variable "node_desired_size" {
  type    = number
  default = "0"
}

variable "node_max_size" {
  type    = number
  default = "1"
}

variable "node_min_size" {
  type    = number
  default = "0"
}

#
# kubectl instance
#

variable "instance_public_key" {
  type    = string
  default = "public-key-path"
}

variable "instance_private_key" {
  type    = string
  default = "private-key-path"
}

variable "instance_iam_instance_profile_name" {
  type    = string
  default = "kubectl_instance_iam_instance_profile"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "instance_subnet_cidr_block" {
  type    = string
  default = "10.0.10.0/24"
}

variable "instance_kubectl_install_url" {
  type    = string
  default = "https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.6/2023-10-17/bin/linux/amd64/kubectl"
}

variable "instance_kubectl_sha_install_url" {
  type    = string
  default = "https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.6/2023-10-17/bin/linux/amd64/kubectl.sha256"
}

variable "instance_sso_role_name" {
  type    = string
  default = "sso role name"
}
