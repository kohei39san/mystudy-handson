output "api_gateway_url" {
  description = "URL of the API Gateway endpoint"
  value       = aws_apigatewayv2_api.slack_api.api_endpoint
}

output "slack_receiver_lambda_arn" {
  description = "ARN of the Slack receiver Lambda function"
  value       = aws_lambda_function.slack_receiver.arn
}

output "mcp_server_lambda_arn" {
  description = "ARN of the MCP server Lambda function"
  value       = aws_lambda_function.mcp_server.arn
}

output "github_to_s3_sync_lambda_arn" {
  description = "ARN of the GitHub to S3 sync Lambda function"
  value       = aws_lambda_function.github_to_s3_sync.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.conversations.name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.data_source.bucket
}

output "opensearch_domain_endpoint" {
  description = "Endpoint of the OpenSearch domain"
  value       = aws_opensearch_domain.vector_store.endpoint
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.mcp_server.repository_url
}