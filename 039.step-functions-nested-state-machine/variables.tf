variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "nested-sfn-study"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "stack_name" {
  description = "CloudFormation stack name"
  type        = string
  default     = "nested-sfn-study-dev"
}
