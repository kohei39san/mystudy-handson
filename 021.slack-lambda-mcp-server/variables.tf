variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for data source"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for conversation history"
  type        = string
  default     = "slack-mcp-conversations"
}

variable "opensearch_domain_name" {
  description = "Name of the OpenSearch domain"
  type        = string
  default     = "slack-mcp-vector-store"
}

variable "opensearch_master_user" {
  description = "Master username for OpenSearch"
  type        = string
  default     = "admin"
}

variable "opensearch_master_password" {
  description = "Master password for OpenSearch"
  type        = string
  sensitive   = true
}

variable "allowed_ip_range" {
  description = "IP range allowed to access OpenSearch"
  type        = string
  default     = "0.0.0.0/0"  # Not recommended for production
}

variable "slack_bot_user_id" {
  description = "Slack bot user ID"
  type        = string
}

variable "bedrock_kb_id" {
  description = "ID of the Bedrock Knowledge Base"
  type        = string
  default     = ""
}

data "aws_caller_identity" "current" {}