resource "aws_lambda_function" "crawler" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "${var.project_name}-crawler"
  role          = aws_iam_role.crawler_lambda.arn
  handler       = "crawl_handler.handler"
  runtime       = "python3.11"

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DATA_SOURCE_ID = aws_cloudformation_stack.bedrock.outputs["DataSourceId"]
    }
  }

  timeout     = 300 # 5分
  memory_size = 256
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/scripts/lambda.zip"
  source_dir  = "${path.module}/scripts"
}

resource "aws_cloudwatch_event_rule" "crawler_schedule" {
  name                = "${var.project_name}-schedule"
  description         = "Schedule for web crawler sync"
  schedule_expression = var.crawling_interval
}

resource "aws_cloudwatch_event_target" "crawler_target" {
  rule      = aws_cloudwatch_event_rule.crawler_schedule.name
  target_id = "CrawlerFunction"
  arn       = aws_lambda_function.crawler.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.crawler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.crawler_schedule.arn
}
