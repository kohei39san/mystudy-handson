variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "apigateway-userpool-payload-test"
}

variable "user_email" {
  description = "Email address for the Cognito user"
  type        = string
  default     = "test@example.com"
}

variable "allowed_ip_addresses" {
  description = "List of IP addresses allowed to access the API Gateway"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Change this to restrict access
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "payload-logger"
}

variable "cognito_user_pool_name" {
  description = "Name of the Cognito User Pool"
  type        = string
  default     = "payload-verification-pool"
}

variable "cognito_user_group_name" {
  description = "Name of the Cognito User Group"
  type        = string
  default     = "api-users"
}

variable "api_gateway_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = "payload-verification-api"
}

variable "cloudformation_template_path" {
  description = "Path to the CloudFormation template"
  type        = string
  default     = "./cfn/infrastructure.yaml"
}