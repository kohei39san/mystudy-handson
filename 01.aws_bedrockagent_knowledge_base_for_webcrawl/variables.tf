variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "t3.small.search"
}

variable "ebs_volume_size" {
  description = "EBS volume size for OpenSearch (GB)"
  type        = number
  default     = 10
}

variable "ebs_volume_type" {
  description = "EBS volume type"
  type        = string
  default     = "gp2"
}

variable "instance_count" {
  description = "Number of OpenSearch instances"
  type        = number
  default     = 1
}

variable "knowledge_base_name" {
  description = "Name of the Bedrock Knowledge Base"
  type        = string
  default     = "webcrawl-knowledge-base"
}

variable "model_arn" {
  description = "ARN of the Claude 3.5 Sonnet v2 model"
  type        = string
  default     = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
}
