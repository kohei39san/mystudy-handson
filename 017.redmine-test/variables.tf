variable "allowed_ip" {
  description = "The IP address allowed to access the Redmine instance"
  type        = string
  default     = "127.0.0.1/32"
}

variable "public_key_path" {
  description = "Path to the public key file to use for SSH access"
  type        = string
  default     = "~/.ssh/id_rsa.pub"  # Added default value
}

variable "instance_type" {
  description = "Path to the public key file to use for SSH access"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "root_volume_size" {
  description = "Size of the root volume in GB"
  type        = number
  default     = 8
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for the subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Name        = "redmine-server"
    Environment = "test"
  }
}