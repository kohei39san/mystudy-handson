output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_cloudformation_stack.game_info_discord_stack.outputs["LambdaFunctionName"]
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_cloudformation_stack.game_info_discord_stack.outputs["LambdaFunctionArn"]
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge rule"
  value       = aws_cloudformation_stack.game_info_discord_stack.outputs["EventBridgeRuleName"]
}