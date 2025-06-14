variable "main_stack_name" {
  description = "Name of the main CloudFormation stack"
  type        = string
}

variable "bedrock_model_id" {
  description = "Bedrock model ID to use for the agent"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "bedrock_opensearch_role_arn" {
  description = "ARN of the role to use for the agent"
  type        = string
  default     = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}

variable "embedding_model_id" {
  description = "Bedrock embedding model ID to use for the knowledge base"
  type        = string
  default     = "amazon.titan-embed-text-v1"
}

variable "opensearch_endpoint" {
  type        = string
  description = "Endpoint of the OpenSearch instance"
  default     = ""
}

variable "opensearch_domain_arn" {
  type        = string
  description = "ARN of the OpenSearch domain"
  default     = ""
}

variable "knowledge_base_bucket_arn" {
  type        = string
  description = "ARN of the knowledge base bucket"
  default     = ""
}