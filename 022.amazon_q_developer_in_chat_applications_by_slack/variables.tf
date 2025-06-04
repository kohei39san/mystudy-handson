variable "slack_workspace_id" {
  description = "The ID of the Slack workspace authorized with AWS Chatbot"
  type        = string
  default     = "T0123456789" # ダミー値
}

variable "slack_channel_id" {
  description = "The ID of the Slack channel where Amazon Q Developer will be used"
  type        = string
  default     = "C0123456789" # ダミー値
}

variable "slack_channel_name" {
  description = "The name of the Slack channel where Amazon Q Developer will be used"
  type        = string
  default     = "aws-chatbot" # ダミー値
}

variable "environment" {
  description = "Environment name for tagging"
  type        = string
  default     = "dev"
}