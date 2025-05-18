resource "aws_cloudformation_stack" "game_info_discord_stack" {
  name = "game-info-discord-stack"

  template_body = file("${path.module}/../src/018.send-game-info-to-discord/cfn/template.yaml")

  parameters = {
    OpenRouterApiKeyParam  = var.openrouter_api_key_param
    DiscordWebhookUrlParam = var.discord_webhook_url_param
    ScheduleExpression     = var.schedule_expression
    LambdaTimeout          = var.lambda_timeout
    LambdaMemorySize       = var.lambda_memory_size
  }

  capabilities = ["CAPABILITY_IAM"]
}

# Create a zip file of the Lambda code
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/../../lambda_function.zip"
  source_dir  = "${path.module}/../../lambda_function"
  excludes    = ["local_test.py", "__pycache__", "*.pyc"]
}

# Update Lambda function code
resource "null_resource" "upload_lambda_code" {
  triggers = {
    lambda_hash = data.archive_file.lambda_zip.output_base64sha256
  }

  provisioner "local-exec" {
    command = <<EOF
      aws lambda update-function-code --function-name ${aws_cloudformation_stack.game_info_discord_stack.outputs["LambdaFunctionName"]} --zip-file fileb://${data.archive_file.lambda_zip.output_path} --region ${var.aws_region} || echo "Lambda function not yet created, will be created by CloudFormation"
    EOF
  }
}