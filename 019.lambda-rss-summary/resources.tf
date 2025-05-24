resource "aws_cloudformation_stack" "rss_summary" {
  name          = "rss-summary-stack"
  template_body = file("${path.module}/../src/019.lambda-rss-summary/template.yaml")
  parameters = {
    OpenRouterApiKeyParam = var.openrouter_api_key_param
    SlackWebhookUrlParam  = var.slack_webhook_url_param
    RssFeedUrl            = var.rss_feed_url
    SummaryPrompt         = var.summary_prompt
    ScheduleExpression    = var.schedule_expression
    LambdaTimeout         = var.lambda_timeout
    LambdaMemorySize      = var.lambda_memory_size
  }
  capabilities = ["CAPABILITY_IAM"]

  tags = {
    "Environment" = "dev"
    "Terraform"   = "true"
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda_function_019.lambda-rss-summary"
  output_path = "${path.module}/../../lambda_function_019.lambda-rss-summary.zip"
  excludes    = ["local_test.py", "__pycache__", "*.pyc"]
}

resource "null_resource" "update_lambda_code" {
  provisioner "local-exec" {
    command = "aws lambda update-function-code --function-name RssSummaryToSlackFunction --zip-file fileb://${path.module}/../../lambda_function_019.lambda-rss-summary.zip"
  }
  triggers = {
    lambda_zip_md5 = data.archive_file.lambda_zip.output_base64sha256
    cfn_stack_id   = aws_cloudformation_stack.rss_summary.id
  }
}
