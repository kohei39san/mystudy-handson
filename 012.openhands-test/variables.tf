variable "allowed_ip" {
  description = "Allowed IP address for SSH access"
  type        = string
  default     = "127.0.0.1/32"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance. If empty, the latest Amazon Linux 2 AMI will be used."
  type        = string
  default     = ""
}
