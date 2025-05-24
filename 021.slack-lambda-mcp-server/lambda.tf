# Slack メッセージを受け取る Lambda 関数の IAM ロール
resource "aws_iam_role" "slack_receiver_role" {
  name = "slack-receiver-lambda-role"

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
    Name    = "slack-receiver-lambda-role"
    Project = var.project_name
  }
}

# Slack メッセージを受け取る Lambda 関数の IAM ポリシー
resource "aws_iam_policy" "slack_receiver_policy" {
  name        = "slack-receiver-lambda-policy"
  description = "Policy for Slack receiver Lambda function"

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
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/slack-bot/*"
        ]
      },
      {
        Action = [
          "sns:Publish"
        ]
        Effect   = "Allow"
        Resource = [
          aws_sns_topic.slack_messages.arn
        ]
      }
    ]
  })
}

# IAM ポリシーをロールにアタッチ
resource "aws_iam_role_policy_attachment" "slack_receiver_policy_attachment" {
  role       = aws_iam_role.slack_receiver_role.name
  policy_arn = aws_iam_policy.slack_receiver_policy.arn
}

# Lambda 基本実行ロールをアタッチ
resource "aws_iam_role_policy_attachment" "slack_receiver_basic_execution_attachment" {
  role       = aws_iam_role.slack_receiver_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# MCP サーバーを実行する Lambda 関数の IAM ロール
resource "aws_iam_role" "mcp_server_role" {
  name = "mcp-server-lambda-role"

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
    Name    = "mcp-server-lambda-role"
    Project = var.project_name
  }
}

# MCP サーバーを実行する Lambda 関数の IAM ポリシー
resource "aws_iam_policy" "mcp_server_policy" {
  name        = "mcp-server-lambda-policy"
  description = "Policy for MCP server Lambda function"

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
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/slack-bot/*",
          "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/openrouter/*"
        ]
      },
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query"
        ]
        Effect   = "Allow"
        Resource = [
          aws_dynamodb_table.conversation_history.arn
        ]
      },
      {
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPost",
          "es:ESHttpPut"
        ]
        Effect   = "Allow"
        Resource = [
          "${aws_opensearch_domain.kb_opensearch.arn}/*"
        ]
      },
      {
        Action = [
          "bedrock:InvokeModel",
          "bedrock:RetrieveAndGenerate",
          "bedrock:GetKnowledgeBase",
          "bedrock:Retrieve",
          "bedrock:ListDataSources",
          "bedrock:ListTagsForResource",
          "bedrock:ListKnowledgeBases",
          "bedrock:Rerank"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "sns:Subscribe",
          "sns:Receive"
        ]
        Effect   = "Allow"
        Resource = [
          aws_sns_topic.slack_messages.arn
        ]
      }
    ]
  })
}

# IAM ポリシーをロールにアタッチ
resource "aws_iam_role_policy_attachment" "mcp_server_policy_attachment" {
  role       = aws_iam_role.mcp_server_role.name
  policy_arn = aws_iam_policy.mcp_server_policy.arn
}

# Lambda 基本実行ロールをアタッチ
resource "aws_iam_role_policy_attachment" "mcp_server_basic_execution_attachment" {
  role       = aws_iam_role.mcp_server_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Slack メッセージを受け取る Lambda 関数のデプロイパッケージ
data "archive_file" "slack_receiver_zip" {
  type        = "zip"
  source_file = "${path.module}/../scripts/021.slack-lambda-mcp-server/js/slack-receiver.js"
  output_path = "${path.module}/../../slack_receiver.zip"
}

# Slack メッセージを受け取る Lambda 関数
resource "aws_lambda_function" "slack_receiver" {
  function_name    = var.slack_receiver_lambda_name
  filename         = data.archive_file.slack_receiver_zip.output_path
  source_code_hash = data.archive_file.slack_receiver_zip.output_base64sha256
  role             = aws_iam_role.slack_receiver_role.arn
  handler          = "slack-receiver.handler"
  runtime          = "nodejs16.x"
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      SLACK_BOT_TOKEN_PARAM       = var.slack_bot_token_param
      SLACK_SIGNING_SECRET_PARAM  = var.slack_signing_secret_param
      SLACK_APP_TOKEN_PARAM       = var.slack_app_token_param
      SNS_TOPIC_ARN               = aws_sns_topic.slack_messages.arn
    }
  }

  tags = {
    Name        = var.slack_receiver_lambda_name
    Environment = "production"
    Project     = var.project_name
  }
}

# Lambda Function URL for Slack receiver
resource "aws_lambda_function_url" "slack_receiver_url" {
  function_name      = aws_lambda_function.slack_receiver.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST"]
    max_age       = 86400
  }
}

# MCP サーバーを実行する Lambda 関数のデプロイパッケージ
data "archive_file" "mcp_server_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../scripts/021.slack-lambda-mcp-server/py"
  output_path = "${path.module}/../../mcp_server_lambda.zip"
}

# MCP サーバーを実行する Lambda 関数
resource "aws_lambda_function" "mcp_server" {
  function_name    = var.mcp_server_lambda_name
  filename         = data.archive_file.mcp_server_zip.output_path
  source_code_hash = data.archive_file.mcp_server_zip.output_base64sha256
  role             = aws_iam_role.mcp_server_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  environment {
    variables = {
      OPENROUTER_API_KEY_PARAM = var.openrouter_api_key_param
      OPENROUTER_MODEL         = var.openrouter_model
      DYNAMODB_TABLE           = aws_dynamodb_table.conversation_history.name
    }
  }

  tags = {
    Name        = var.mcp_server_lambda_name
    Environment = "production"
    Project     = var.project_name
  }
}

# SNS サブスクリプション
resource "aws_sns_subscription" "mcp_server_subscription" {
  topic_arn = aws_sns_topic.slack_messages.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.mcp_server.arn
}

# Lambda 関数に SNS からの呼び出しを許可
resource "aws_lambda_permission" "allow_sns_to_invoke_mcp_server" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mcp_server.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.slack_messages.arn
}

# GitHub から S3 に同期する Lambda 関数の IAM ロール
resource "aws_iam_role" "github_sync_role" {
  name = "github-sync-lambda-role"

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
    Name    = "github-sync-lambda-role"
    Project = var.project_name
  }
}

# GitHub から S3 に同期する Lambda 関数の IAM ポリシー
resource "aws_iam_policy" "github_sync_policy" {
  name        = "github-sync-lambda-policy"
  description = "Policy for GitHub to S3 sync Lambda function"

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
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/github/*"
        ]
      },
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.data_bucket.arn,
          "${aws_s3_bucket.data_bucket.arn}/*"
        ]
      },
      {
        Action = [
          "bedrock:StartIngestionJob"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# IAM ポリシーをロールにアタッチ
resource "aws_iam_role_policy_attachment" "github_sync_policy_attachment" {
  role       = aws_iam_role.github_sync_role.name
  policy_arn = aws_iam_policy.github_sync_policy.arn
}

# Lambda 基本実行ロールをアタッチ
resource "aws_iam_role_policy_attachment" "github_sync_basic_execution_attachment" {
  role       = aws_iam_role.github_sync_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# GitHub から S3 に同期する Lambda 関数のデプロイパッケージ
data "archive_file" "github_sync_zip" {
  type        = "zip"
  source_file = "${path.module}/../scripts/021.slack-lambda-mcp-server/py/github_to_s3_sync.py"
  output_path = "${path.module}/../../github_to_s3_sync.zip"
}

# GitHub から S3 に同期する Lambda 関数
resource "aws_lambda_function" "github_to_s3_sync" {
  function_name    = var.github_sync_lambda_name
  filename         = data.archive_file.github_sync_zip.output_path
  source_code_hash = data.archive_file.github_sync_zip.output_base64sha256
  role             = aws_iam_role.github_sync_role.arn
  handler          = "github_to_s3_sync.lambda_handler"
  runtime          = "python3.9"
  timeout          = 300
  memory_size      = 512

  environment {
    variables = {
      S3_BUCKET_NAME        = aws_s3_bucket.data_bucket.id
      S3_PREFIX             = "docs/"
      GITHUB_REPO_URL_PARAM = var.github_repo_url_param
      GITHUB_USERNAME_PARAM = var.github_username_param
      GITHUB_TOKEN_PARAM    = var.github_token_param
    }
  }

  tags = {
    Name        = var.github_sync_lambda_name
    Environment = "production"
    Project     = var.project_name
  }
}