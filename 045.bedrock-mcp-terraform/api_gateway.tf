data "archive_file" "api_adapter" {
  type        = "zip"
  source_file = "${path.module}/scripts/api_adapter.py"
  output_path = "${path.module}/.terraform/api_adapter.zip"
}

resource "aws_cloudwatch_log_group" "api_adapter" {
  name              = "/aws/lambda/${local.name_prefix}-api-adapter"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "api_adapter" {
  function_name    = "${local.name_prefix}-api-adapter"
  role             = aws_iam_role.api_adapter.arn
  runtime          = "python3.12"
  handler          = "api_adapter.handler"
  filename         = data.archive_file.api_adapter.output_path
  source_code_hash = data.archive_file.api_adapter.output_base64sha256
  timeout          = 60

  environment {
    variables = {
      AGENTCORE_RUNTIME_ARN = aws_bedrockagentcore_agent_runtime.this.agent_runtime_arn
    }
  }

  depends_on = [aws_cloudwatch_log_group.api_adapter]
}

resource "aws_apigatewayv2_api" "inquiry" {
  name          = "${local.name_prefix}-inquiry"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "inquiry" {
  api_id                 = aws_apigatewayv2_api.inquiry.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api_adapter.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "inquiry" {
  api_id             = aws_apigatewayv2_api.inquiry.id
  route_key          = "POST /invoke"
  target             = "integrations/${aws_apigatewayv2_integration.inquiry.id}"
  authorization_type = local.api_authorization_type
}

resource "aws_apigatewayv2_stage" "inquiry" {
  api_id      = aws_apigatewayv2_api.inquiry.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_access.arn
    format          = "$context.requestId $context.status $context.integrationErrorMessage"
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_adapter.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.inquiry.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "api_access" {
  name              = "/aws/apigateway/${local.name_prefix}-inquiry"
  retention_in_days = var.log_retention_days
}
