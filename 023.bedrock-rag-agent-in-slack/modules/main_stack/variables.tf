variable "project_name" {
  description = "Name of the project"
  type        = string
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