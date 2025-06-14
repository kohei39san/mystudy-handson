output "slack_channel_configuration_arn" {
  description = "ARN of the Slack Channel Configuration"
  value       = aws_cloudformation_stack.main_stack.outputs["SlackChannelConfigurationArn"]
}

output "iam_role_arn" {
  description = "ARN of the IAM Role for Bedrock Agent in Slack"
  value       = aws_cloudformation_stack.main_stack.outputs["IAMRoleArn"]
}

output "bedrock_opensearch_role_arn" {
  description = "ARN of the IAM Role for Bedrock to access OpenSearch"
  value       = aws_cloudformation_stack.main_stack.outputs["BedrockOpenSearchRoleArn"]
}

output "opensearch_domain_arn" {
  description = "ARN of the OpenSearch Domain"
  value       = aws_cloudformation_stack.main_stack.outputs["OpenSearchDomainArn"]
}

output "opensearch_endpoint" {
  description = "Endpoint of the OpenSearch Domain"
  value       = aws_cloudformation_stack.main_stack.outputs["OpenSearchDomainEndpoint"]
}

output "knowledge_base_bucket_name" {
  description = "Name of the S3 Bucket for Knowledge Base Documents"
  value       = aws_cloudformation_stack.main_stack.outputs["KnowledgeBaseBucketName"]
}

output "knowledge_base_bucket_arn" {
  description = "ARN of the S3 Bucket for Knowledge Base Documents"
  value       = aws_cloudformation_stack.main_stack.outputs["KnowledgeBaseBucketArn"]
}