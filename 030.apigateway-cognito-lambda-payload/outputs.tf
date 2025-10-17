output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cloudformation_stack.infrastructure.outputs["CognitoUserPoolId"]
}

output "cognito_user_pool_client_id" {
  description = "ID of the Cognito User Pool Client"
  value       = aws_cloudformation_stack.infrastructure.outputs["CognitoUserPoolClientId"]
}

output "cognito_user_pool_domain" {
  description = "Domain of the Cognito User Pool"
  value       = aws_cloudformation_stack.infrastructure.outputs["CognitoUserPoolDomain"]
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = aws_cloudformation_stack.infrastructure.outputs["ApiGatewayUrl"]
}

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_cloudformation_stack.infrastructure.outputs["ApiGatewayId"]
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_cloudformation_stack.infrastructure.outputs["LambdaFunctionName"]
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_cloudformation_stack.infrastructure.outputs["LambdaFunctionArn"]
}

output "cognito_user_arn" {
  description = "ARN of the created Cognito user"
  value       = aws_cloudformation_stack.infrastructure.outputs["CognitoUserArn"]
}

output "iam_role_arn" {
  description = "ARN of the IAM role for Cognito users"
  value       = aws_cloudformation_stack.infrastructure.outputs["CognitoUserRoleArn"]
}

output "cloudformation_stack_id" {
  description = "ID of the CloudFormation stack"
  value       = aws_cloudformation_stack.infrastructure.id
}

output "deployment_info" {
  description = "Deployment information and next steps"
  value = {
    user_pool_id     = aws_cloudformation_stack.infrastructure.outputs["CognitoUserPoolId"]
    client_id        = aws_cloudformation_stack.infrastructure.outputs["CognitoUserPoolClientId"]
    api_url          = aws_cloudformation_stack.infrastructure.outputs["ApiGatewayUrl"]
    user_email       = var.user_email
    next_steps = [
      "1. Set temporary password for user: aws cognito-idp admin-set-user-password --user-pool-id ${aws_cloudformation_stack.infrastructure.outputs["CognitoUserPoolId"]} --username ${var.user_email} --password 'TempPassword123!' --permanent",
      "2. Test authentication with the Cognito User Pool",
      "3. Use the JWT token to call the API Gateway endpoint",
      "4. Check CloudWatch Logs for Lambda function output"
    ]
  }
}