variable "aws_region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used in resource names and tags."
  type        = string
  default     = "bedrock-mcp"
}

variable "agentcore_runtime_name" {
  type    = string
  default = "bedrock-mcp-runtime"
}

variable "agent_image_tag" {
  description = "Docker image tag pushed to ECR and deployed to AgentCore Runtime."
  type        = string
  default     = "latest"
}

variable "agentcore_gateway_name" {
  description = "AgentCore Gateway name managed by the AWS provider."
  type        = string
  default     = "bedrock-mcp-gateway"
}

variable "github_mcp_endpoint" {
  description = "Official GitHub MCP Server remote HTTPS endpoint."
  type        = string
  default     = "https://api.githubcopilot.com/mcp/"
}

variable "github_oauth_client_id" {
  description = "GitHub OAuth App client ID used to create the AgentCore credential provider."
  type        = string
}

variable "github_oauth_client_secret" {
  description = "GitHub OAuth App client secret. Do not commit the value or tfvars file."
  type        = string
  sensitive   = true
}

variable "api_authorizer_type" {
  description = "Authentication mode for the HTTP API."
  type        = string
  default     = "AWS_IAM"

  validation {
    condition     = contains(["NONE", "AWS_IAM"], var.api_authorizer_type)
    error_message = "api_authorizer_type must be NONE or AWS_IAM."
  }
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention period."
  type        = number
  default     = 14
}
