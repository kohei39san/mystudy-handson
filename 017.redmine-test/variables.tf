variable "allowed_ip" {
  description = "The IP address allowed to access the Redmine instance"
  type        = string
  default     = "127.0.0.1/32"
}

variable "public_key_path" {
  description = "Path to the public key file to use for SSH access"
  type        = string
  default     = "../src/017.redmine-test/id_rsa.dummy.pub" # Added default value
}

variable "private_key_path" {
  description = "Path to the private key file to use for SSH access"
  type        = string
  default     = "~/.ssh/id_rsa" # Default private key path
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "root_volume_size" {
  description = "Size of the root volume in GB"
  type        = number
  default     = 10
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

variable "security_group_name" {
  description = "security group name"
  type        = string
  default     = "redmine-security-group-name"
}

variable "user_data_path" {
  description = "redmine user data path"
  type        = string
  default     = "../scripts/017.redmine-test/userdata.sh"
}

variable "sg_eice_name" {
  description = "redmine sg eice name"
  type        = string
  default     = "redmine-eice"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Name        = "redmine-server"
    Environment = "test"
  }
}