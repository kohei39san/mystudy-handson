output "lambda_function_arn" {
  description = "ARN of the GitHub to S3 Sync Lambda Function"
  value       = aws_cloudformation_stack.lambda_stack.outputs["LambdaFunctionArn"]
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge Rule"
  value       = aws_cloudformation_stack.lambda_stack.outputs["EventBridgeRuleArn"]
}