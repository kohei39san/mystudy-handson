variable "aws_tags" {
  type    = map(string)
  default = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging resources"
  default     = "dev"
}