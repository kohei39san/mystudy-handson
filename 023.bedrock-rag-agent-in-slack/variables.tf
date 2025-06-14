variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "bedrock-slack-chat"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "slack_workspace_id" {
  description = "ID of the Slack workspace"
  type        = string
}

variable "slack_channel_id" {
  description = "ID of the Slack channel"
  type        = string
}

variable "slack_channel_name" {
  description = "Name of the Slack channel"
  type        = string
}

variable "opensearch_instance_type" {
  description = "Instance type for OpenSearch cluster"
  type        = string
  default     = "t3.small.search"
}

variable "bedrock_model_id" {
  description = "Bedrock model ID to use for the agent"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20240620-v1:0"
}

variable "embedding_model_id" {
  description = "Bedrock embedding model ID to use for the knowledge base"
  type        = string
  default     = "amazon.titan-embed-text-v1"
}

variable "github_repository_url" {
  description = "URL of the GitHub repository to sync"
  type        = string
  sensitive   = true
}

variable "github_pat" {
  description = "GitHub Personal Access Token"
  type        = string
  sensitive   = true
}

variable "github_username" {
  description = "GitHub username"
  type        = string
  sensitive   = true
}

variable "schedule_expression" {
  description = "Schedule expression for the EventBridge rule"
  type        = string
  default     = "rate(1 hour)"
}