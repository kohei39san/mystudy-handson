provider "aws" {
  region = var.aws_region
}

# SNSトピックの作成
resource "aws_sns_topic" "slack_messages" {
  name = "slack-messages-topic"
}

# CloudFormationスタックの作成（Bedrock Knowledge Base用）
resource "aws_cloudformation_stack" "bedrock_kb" {
  name = "bedrock-knowledge-base-stack"
  template_body = file("${path.module}/../src/021.slack-lambda-mcp-server/cfn/bedrock-kb-cfn.yaml")
  
  parameters = {
    OpenSearchDomainName = var.opensearch_domain_name
    OpenSearchDomainArn  = aws_opensearch_domain.kb_opensearch.arn
    S3BucketName         = var.s3_bucket_name
    S3BucketArn          = aws_s3_bucket.data_bucket.arn
    S3RoleArn            = aws_iam_role.bedrock_s3_role.arn
    OpenSearchRoleArn    = aws_iam_role.bedrock_opensearch_role.arn
    KnowledgeBaseRoleArn = aws_iam_role.bedrock_kb_role.arn
  }
  
  depends_on = [
    aws_opensearch_domain.kb_opensearch,
    aws_s3_bucket.data_bucket,
    aws_iam_role.bedrock_s3_role,
    aws_iam_role.bedrock_opensearch_role,
    aws_iam_role.bedrock_kb_role
  ]
}

# EventBridge スケジュールルールの作成
resource "aws_scheduler_schedule" "github_sync_schedule" {
  name       = "github-sync-schedule"
  schedule_expression = "rate(1 day)"
  
  target {
    arn      = aws_lambda_function.github_to_s3_sync.arn
    role_arn = aws_iam_role.eventbridge_invoke_lambda_role.arn
  }

  flexible_time_window {
    mode = "OFF"
  }
}

# EventBridge が Lambda を呼び出すための IAM ロール
resource "aws_iam_role" "eventbridge_invoke_lambda_role" {
  name = "eventbridge-invoke-lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })
}

# EventBridge が Lambda を呼び出すための IAM ポリシー
resource "aws_iam_policy" "eventbridge_invoke_lambda_policy" {
  name        = "eventbridge-invoke-lambda-policy"
  description = "Policy for EventBridge to invoke Lambda functions"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.github_to_s3_sync.arn
      }
    ]
  })
}

# IAM ポリシーをロールにアタッチ
resource "aws_iam_role_policy_attachment" "eventbridge_lambda_policy_attachment" {
  role       = aws_iam_role.eventbridge_invoke_lambda_role.name
  policy_arn = aws_iam_policy.eventbridge_invoke_lambda_policy.arn
}

# Lambda 関数に EventBridge からの呼び出しを許可
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.github_to_s3_sync.function_name
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.github_sync_schedule.arn
}

# SSM パラメータの作成
resource "aws_ssm_parameter" "slack_bot_token" {
  name        = "/slack-bot/token"
  description = "Slack Bot Token"
  type        = "SecureString"
  value       = "dummy-value-replace-me"  # デプロイ後に実際の値に更新する
  
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "slack_signing_secret" {
  name        = "/slack-bot/signing-secret"
  description = "Slack Signing Secret"
  type        = "SecureString"
  value       = "dummy-value-replace-me"  # デプロイ後に実際の値に更新する
  
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "slack_app_token" {
  name        = "/slack-bot/app-token"
  description = "Slack App Token"
  type        = "SecureString"
  value       = "dummy-value-replace-me"  # デプロイ後に実際の値に更新する
  
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "openrouter_api_key" {
  name        = "/openrouter/api-key"
  description = "OpenRouter API Key"
  type        = "SecureString"
  value       = "dummy-value-replace-me"  # デプロイ後に実際の値に更新する
  
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "github_repo_url" {
  name        = "/github/repo-url"
  description = "GitHub Repository URL"
  type        = "String"
  value       = "https://github.com/username/repo.git"  # デプロイ後に実際の値に更新する
  
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "github_username" {
  name        = "/github/username"
  description = "GitHub Username"
  type        = "String"
  value       = "username"  # デプロイ後に実際の値に更新する
  
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "github_token" {
  name        = "/github/token"
  description = "GitHub Personal Access Token"
  type        = "SecureString"
  value       = "dummy-value-replace-me"  # デプロイ後に実際の値に更新する
  
  lifecycle {
    ignore_changes = [value]
  }
}