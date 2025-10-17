locals {
  stack_name = "${var.project_name}-${var.environment}"
}

# CloudFormation stack for the infrastructure
resource "aws_cloudformation_stack" "infrastructure" {
  name         = local.stack_name
  template_body = file(var.cloudformation_template_path)
  
  parameters = {
    Environment            = var.environment
    ProjectName           = var.project_name
    UserEmail             = var.user_email
    LambdaFunctionName    = var.lambda_function_name
    CognitoUserPoolName   = var.cognito_user_pool_name
    CognitoUserGroupName  = var.cognito_user_group_name
    ApiGatewayName        = var.api_gateway_name
    AllowedIpAddresses    = join(",", var.allowed_ip_addresses)
  }
  
  capabilities = ["CAPABILITY_IAM"]
  
  tags = {
    Name        = local.stack_name
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
    Terraform   = "true"
  }
}