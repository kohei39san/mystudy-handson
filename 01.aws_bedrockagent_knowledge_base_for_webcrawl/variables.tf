variable "embedding_model_arn" {
  description = "ARN of the Bedrock embedding model"
  type        = string
  default     = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "t3.small.elasticsearch"
}
