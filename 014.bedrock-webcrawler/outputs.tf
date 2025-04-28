output "opensearch_endpoint" {
  description = "OpenSearchドメインエンドポイント"
  value       = aws_opensearch_domain.vector_store.endpoint
}

output "lambda_function_name" {
  description = "Lambda関数名"
  value       = aws_lambda_function.crawler.function_name
}

output "eventbridge_schedule" {
  description = "EventBridgeスケジュール"
  value       = aws_cloudwatch_event_rule.crawler_schedule.schedule_expression
}
