output "slack_channel_configuration_arn" {
  description = "ARN of the Slack Channel Configuration"
  value       = module.main_stack.slack_channel_configuration_arn
}

output "iam_role_arn" {
  description = "ARN of the IAM Role for Bedrock Agent in Slack"
  value       = module.main_stack.iam_role_arn
}

output "bedrock_opensearch_role_arn" {
  description = "ARN of the IAM Role for Bedrock to access OpenSearch"
  value       = module.main_stack.bedrock_opensearch_role_arn
}

output "opensearch_domain_arn" {
  description = "ARN of the OpenSearch Domain"
  value       = module.main_stack.opensearch_domain_arn
}

output "opensearch_domain_endpoint" {
  description = "Endpoint of the OpenSearch Domain"
  value       = module.main_stack.opensearch_endpoint
}

output "knowledge_base_bucket_name" {
  description = "Name of the S3 Bucket for Knowledge Base Documents"
  value       = module.main_stack.knowledge_base_bucket_name
}

output "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID"
  value       = module.bedrock_stack.knowledge_base_id
}

output "data_source_id" {
  description = "Bedrock Data Source ID"
  value       = module.bedrock_stack.data_source_id
}

output "agent_id" {
  description = "Bedrock Agent ID"
  value       = module.bedrock_stack.agent_id
}

output "agent_alias_id" {
  description = "Bedrock Agent Alias ID"
  value       = module.bedrock_stack.agent_alias_id
}

output "lambda_function_arn" {
  description = "ARN of the GitHub to S3 Sync Lambda Function"
  value       = module.lambda_stack.lambda_function_arn
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge Rule"
  value       = module.lambda_stack.eventbridge_rule_arn
}

output "slack_connect_agent" {
  description = "ARN of the Slack Connect Agent"
  value       = "@Amazon Q connector add agent ${module.bedrock_stack.agent_arn} ${module.bedrock_stack.alias_id}"
}