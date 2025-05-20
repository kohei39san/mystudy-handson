# ---------------------------------------------------------------------------------------------------------------------
# IAM Role for Lambda Functions
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "lambda_role" {
  name = "slack_mcp_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "Slack MCP Lambda Role"
    Environment = var.environment
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "slack_mcp_lambda_policy"
  description = "Policy for Slack MCP Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.conversations.arn
      },
      {
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/slack-mcp-bot/*"
      },
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.data_source.arn,
          "${aws_s3_bucket.data_source.arn}/*"
        ]
      },
      {
        Action = [
          "bedrock:InvokeModel",
          "bedrock:RetrieveAndGenerate"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# ---------------------------------------------------------------------------------------------------------------------
# Slack Receiver Lambda Function
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_lambda_function" "slack_receiver" {
  function_name    = "slack_mcp_receiver"
  role             = aws_iam_role.lambda_role.arn
  handler          = "slack-receiver.handler"
  runtime          = "nodejs18.x"
  timeout          = 30
  memory_size      = 256
  
  filename         = data.archive_file.slack_receiver_zip.output_path
  source_code_hash = data.archive_file.slack_receiver_zip.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE    = aws_dynamodb_table.conversations.name
      MCP_SERVER_LAMBDA = aws_lambda_function.mcp_server.function_name
      BOT_USER_ID       = var.slack_bot_user_id
    }
  }

  tags = {
    Name        = "Slack MCP Receiver"
    Environment = var.environment
  }
}

data "archive_file" "slack_receiver_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../scripts/021.slack-lambda-mcp-server/js"
  output_path = "${path.module}/slack_receiver.zip"
}

# ---------------------------------------------------------------------------------------------------------------------
# MCP Server Lambda Function
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_lambda_function" "mcp_server" {
  function_name    = "slack_mcp_server"
  role             = aws_iam_role.lambda_role.arn
  package_type     = "Image"
  timeout          = 60
  memory_size      = 1024
  
  image_uri        = "${aws_ecr_repository.mcp_server.repository_url}:latest"

  environment {
    variables = {
      DYNAMODB_TABLE         = aws_dynamodb_table.conversations.name
      AWS_DOCS_MCP_SERVER_PORT = "8080"
      BEDROCK_KB_MCP_SERVER_PORT = "8081"
      BEDROCK_KB_ID          = var.bedrock_kb_id
    }
  }

  tags = {
    Name        = "Slack MCP Server"
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# GitHub to S3 Sync Lambda Function
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_lambda_function" "github_to_s3_sync" {
  function_name    = "github_to_s3_sync"
  role             = aws_iam_role.lambda_role.arn
  handler          = "github_to_s3_sync.handler"
  runtime          = "python3.11"
  timeout          = 300
  memory_size      = 512
  
  filename         = data.archive_file.github_to_s3_sync_zip.output_path
  source_code_hash = data.archive_file.github_to_s3_sync_zip.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.data_source.bucket
      S3_PREFIX      = "github-sync"
    }
  }

  tags = {
    Name        = "GitHub to S3 Sync"
    Environment = var.environment
  }
}

data "archive_file" "github_to_s3_sync_zip" {
  type        = "zip"
  source_file = "${path.module}/../scripts/021.slack-lambda-mcp-server/py/github_to_s3_sync.py"
  output_path = "${path.module}/github_to_s3_sync.zip"
}

# ---------------------------------------------------------------------------------------------------------------------
# API Gateway for Slack Events
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_apigatewayv2_api" "slack_api" {
  name          = "slack-mcp-api"
  protocol_type = "HTTP"

  tags = {
    Name        = "Slack MCP API"
    Environment = var.environment
  }
}

resource "aws_apigatewayv2_stage" "slack_api" {
  api_id      = aws_apigatewayv2_api.slack_api.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Name        = "Slack MCP API Stage"
    Environment = var.environment
  }
}

resource "aws_apigatewayv2_integration" "slack_api" {
  api_id             = aws_apigatewayv2_api.slack_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.slack_receiver.invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "slack_api" {
  api_id    = aws_apigatewayv2_api.slack_api.id
  route_key = "POST /"
  target    = "integrations/${aws_apigatewayv2_integration.slack_api.id}"
}

resource "aws_lambda_permission" "slack_api" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slack_receiver.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.slack_api.execution_arn}/*/*"
}

# ---------------------------------------------------------------------------------------------------------------------
# EventBridge Rule for GitHub to S3 Sync
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "github_sync" {
  name                = "github-to-s3-sync-schedule"
  description         = "Trigger GitHub to S3 sync Lambda function"
  schedule_expression = "rate(1 hour)"

  tags = {
    Name        = "GitHub to S3 Sync Schedule"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "github_sync" {
  rule      = aws_cloudwatch_event_rule.github_sync.name
  target_id = "github_to_s3_sync"
  arn       = aws_lambda_function.github_to_s3_sync.arn
}

resource "aws_lambda_permission" "github_sync" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.github_to_s3_sync.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.github_sync.arn
}

# ---------------------------------------------------------------------------------------------------------------------
# ECR Repository for MCP Server Lambda
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_ecr_repository" "mcp_server" {
  name                 = "slack-mcp-server"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "Slack MCP Server Repository"
    Environment = var.environment
  }
}