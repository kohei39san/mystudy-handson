variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "slack-mcp-bot"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for data storage"
  type        = string
  default     = "slack-mcp-bot-data"
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for conversation history"
  type        = string
  default     = "slack-mcp-bot-conversations"
}

variable "opensearch_domain_name" {
  description = "Name of the OpenSearch domain"
  type        = string
  default     = "slack-mcp-bot-opensearch"
}

variable "opensearch_instance_type" {
  description = "Instance type for OpenSearch"
  type        = string
  default     = "t3.small.search" # 最小コストのインスタンスタイプ
}

variable "opensearch_instance_count" {
  description = "Number of instances in the OpenSearch cluster"
  type        = number
  default     = 1 # 最小構成
}

variable "opensearch_ebs_volume_size" {
  description = "Size of the EBS volume for OpenSearch in GB"
  type        = number
  default     = 10 # 最小サイズ
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda functions in MB"
  type        = number
  default     = 1024
}

variable "lambda_timeout" {
  description = "Timeout for Lambda functions in seconds"
  type        = number
  default     = 900 # 15分（最大値）
}

variable "slack_receiver_lambda_name" {
  description = "Name of the Lambda function for receiving Slack messages"
  type        = string
  default     = "slack-receiver-lambda"
}

variable "mcp_server_lambda_name" {
  description = "Name of the Lambda function for running MCP server"
  type        = string
  default     = "mcp-server-lambda"
}

variable "github_sync_lambda_name" {
  description = "Name of the Lambda function for syncing GitHub to S3"
  type        = string
  default     = "github-to-s3-sync-lambda"
}

variable "openrouter_model" {
  description = "OpenRouter model to use"
  type        = string
  default     = "anthropic/claude-3-opus:beta"
}

variable "github_repo_url_param" {
  description = "SSM Parameter Store key for GitHub repository URL"
  type        = string
  default     = "/github/repo-url"
}

variable "github_username_param" {
  description = "SSM Parameter Store key for GitHub username"
  type        = string
  default     = "/github/username"
}

variable "github_token_param" {
  description = "SSM Parameter Store key for GitHub token"
  type        = string
  default     = "/github/token"
}

variable "slack_bot_token_param" {
  description = "SSM Parameter Store key for Slack bot token"
  type        = string
  default     = "/slack-bot/token"
}

variable "slack_signing_secret_param" {
  description = "SSM Parameter Store key for Slack signing secret"
  type        = string
  default     = "/slack-bot/signing-secret"
}

variable "slack_app_token_param" {
  description = "SSM Parameter Store key for Slack app token"
  type        = string
  default     = "/slack-bot/app-token"
}

variable "openrouter_api_key_param" {
  description = "SSM Parameter Store key for OpenRouter API key"
  type        = string
  default     = "/openrouter/api-key"
}