resource "aws_cloudformation_stack" "game_info_discord_stack" {
  name = "game-info-discord-stack"
  
  template_body = file("${path.module}/../src/018.send-game-info-to-discord/template.yaml")
  
  parameters = {
    OpenRouterApiKeyParam  = var.openrouter_api_key_param
    DiscordWebhookUrlParam = var.discord_webhook_url_param
    ScheduleExpression     = var.schedule_expression
    LambdaTimeout          = var.lambda_timeout
    LambdaMemorySize       = var.lambda_memory_size
  }
  
  capabilities = ["CAPABILITY_IAM"]
  
  # Upload Lambda code before deploying CloudFormation
  depends_on = [null_resource.upload_lambda_code]
}

# Create a zip file of the Lambda code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../scripts/018.send-game-info-to-discord"
  output_path = "${path.module}/lambda_function.zip"
  excludes    = ["local_test.py", "__pycache__", "*.pyc"]
}

# Upload Lambda code to S3
resource "aws_s3_bucket" "lambda_code_bucket" {
  bucket_prefix = "game-info-lambda-code-"
  force_destroy = true
}

resource "aws_s3_object" "lambda_code" {
  bucket = aws_s3_bucket.lambda_code_bucket.id
  key    = "lambda_function.zip"
  source = data.archive_file.lambda_zip.output_path
  etag   = filemd5(data.archive_file.lambda_zip.output_path)
}

# Update Lambda function code
resource "null_resource" "upload_lambda_code" {
  triggers = {
    lambda_hash = data.archive_file.lambda_zip.output_base64sha256
  }

  provisioner "local-exec" {
    command = <<EOF
      aws lambda update-function-code \
        --function-name GameInfoToDiscordFunction \
        --s3-bucket ${aws_s3_object.lambda_code.bucket} \
        --s3-key ${aws_s3_object.lambda_code.key} \
        --region ${var.aws_region} || echo "Lambda function not yet created, will be created by CloudFormation"
    EOF
  }

  depends_on = [aws_s3_object.lambda_code]
}