variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-northeast-1"  # Tokyo region
}

variable "openrouter_api_key_param" {
  description = "SSM Parameter Store name for OpenRouter API key"
  type        = string
  default     = "/game-info/openrouter-api-key"
}

variable "discord_webhook_url_param" {
  description = "SSM Parameter Store name for Discord webhook URL"
  type        = string
  default     = "/game-info/discord-webhook-url"
}

variable "schedule_expression" {
  description = "Schedule expression for the EventBridge rule"
  type        = string
  default     = "cron(0 0 ? * SUN *)"  # Every Sunday at midnight
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 128
}