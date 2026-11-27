output "api_endpoint" {
  description = "API Gateway endpoint for the inquiry API."
  value       = aws_apigatewayv2_api.inquiry.api_endpoint
}

output "api_invoke_url" {
  description = "POST endpoint for agent inquiries."
  value       = "${aws_apigatewayv2_api.inquiry.api_endpoint}/invoke"
}

output "api_adapter_lambda_arn" {
  description = "Lambda adapter ARN."
  value       = aws_lambda_function.api_adapter.arn
}

output "api_authorization_type" {
  description = "Authentication mode applied to the HTTP API route."
  value       = local.api_authorization_type
}

output "agentcore_runtime_arn" {
  description = "AgentCore Runtime ARN managed by the AWS provider."
  value       = aws_bedrockagentcore_agent_runtime.this.agent_runtime_arn
}

output "agentcore_gateway_endpoint" {
  description = "AgentCore Gateway endpoint managed by the AWS provider."
  value       = aws_bedrockagentcore_gateway.this.gateway_url
}
