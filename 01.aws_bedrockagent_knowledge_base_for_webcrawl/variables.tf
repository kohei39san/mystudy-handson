variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
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

variable "storage_size" {
  description = "EBS volume size for OpenSearch (in GB)"
  type        = number
  default     = 10
}

variable "bedrock_model_id" {
  description = "Bedrock model ID for knowledge base"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20240620-v2:0"
}

variable "web_crawler_urls" {
  description = "List of URLs for web crawling"
  type        = list(string)
  default     = ["https://example.com"]
}
