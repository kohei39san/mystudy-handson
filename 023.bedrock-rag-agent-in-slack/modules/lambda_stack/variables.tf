variable "main_stack_name" {
  description = "Name of the main CloudFormation stack"
  type        = string
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

variable "knowledgebase_bucket_arn" {
  description = "ARN of the knowledgebase bucket"
  type        = string
  default     = null
}

variable "knowledgebase_bucket_name" {
  description = "Name of the knowledgebase bucket"
  type        = string
  default     = null
}

variable "knowledgebase_id" {
  description = "ID of the knowledgebase"
  type        = string
  default     = null
}

variable "datasource_id" {
  description = "ID of the data source"
  type        = string
  default     = null
}