# https://developer.hashicorp.com/terraform/language/values/variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "knowledge_base_name" {
  description = "Name of the Bedrock Knowledge Base"
  type        = string
  default     = "webcrawl-knowledge-base"
}

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "t3.small.search"
}

variable "opensearch_version" {
  description = "OpenSearch version"
  type        = string
  default     = "2.11"
}
