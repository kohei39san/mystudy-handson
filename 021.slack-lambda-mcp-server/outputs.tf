output "slack_receiver_function_url" {
  description = "URL for the Slack receiver Lambda function"
  value       = aws_lambda_function_url.slack_receiver_url.function_url
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for conversation history"
  value       = aws_dynamodb_table.conversation_history.name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for data storage"
  value       = aws_s3_bucket.data_bucket.id
}

output "opensearch_domain_endpoint" {
  description = "Endpoint of the OpenSearch domain"
  value       = aws_opensearch_domain.kb_opensearch.endpoint
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.mcp_server_repo.repository_url
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for Lambda communication"
  value       = aws_sns_topic.slack_messages.arn
}

output "cloudformation_stack_name" {
  description = "Name of the CloudFormation stack for Bedrock Knowledge Base"
  value       = aws_cloudformation_stack.bedrock_kb.name
}

output "next_steps" {
  description = "Next steps after deployment"
  value       = <<-EOT
    1. Update the Slack app manifest file with the Lambda function URL:
       - Replace ${LAMBDA_FUNCTION_URL} with: ${aws_lambda_function_url.slack_receiver_url.function_url}
    
    2. Create a Slack app using the manifest file at:
       - src/021.slack-lambda-mcp-server/slack-app.json
    
    3. Set up the required parameters in AWS Systems Manager Parameter Store:
       - /slack-bot/token
       - /slack-bot/signing-secret
       - /slack-bot/app-token
       - /openrouter/api-key
       - /github/repo-url
       - /github/username
       - /github/token
  EOT
}