# 現在のAWSアカウントIDを取得
data "aws_caller_identity" "current" {}

# Lambda用IAMロール
resource "aws_iam_role" "crawler_lambda" {
  name = "${var.project_name}-crawler-role"

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
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.crawler_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Bedrock呼び出し用のポリシー
resource "aws_iam_policy" "bedrock_invoke_model" {
  name        = "${var.project_name}-bedrock-invoke-model"
  description = "Allow invoking Bedrock models and managing data sources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvokeModelStatement"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:StartDataSourceSubsequentCrawl",
          "bedrock:GetDataSourceSubsequentCrawl"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_bedrock" {
  role       = aws_iam_role.crawler_lambda.name
  policy_arn = aws_iam_policy.bedrock_invoke_model.arn
}

# BedrockとOpenSearchの連携用のIAMロール
resource "aws_iam_role" "bedrock_opensearch" {
  name = "${var.project_name}-bedrock-opensearch-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
      }
    ]
  })
}

# OpenSearch操作用のポリシー
resource "aws_iam_policy" "bedrock_opensearch_access" {
  name        = "${var.project_name}-bedrock-opensearch-access"
  description = "Allow Bedrock to access OpenSearch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPut",
          "es:ESHttpPost",
          "es:ESHttpDelete",
          "es:DescribeDomain"
        ]
        Resource = [
          aws_opensearch_domain.vector_store.arn,
          "${aws_opensearch_domain.vector_store.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bedrock_opensearch" {
  role       = aws_iam_role.bedrock_opensearch.name
  policy_arn = aws_iam_policy.bedrock_opensearch_access.arn
}

# OpenSearchプロバイダー用のIAMロール
resource "aws_iam_role" "opensearch_provider" {
  name = "${var.project_name}-opensearch-provider-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
      }
    ]
  })
}

# OpenSearchプロバイダー用のポリシー
resource "aws_iam_policy" "opensearch_provider_access" {
  name        = "${var.project_name}-opensearch-provider-access"
  description = "Allow OpenSearch provider to manage indices"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPut",
          "es:ESHttpPost",
          "es:ESHttpDelete"
        ]
        Resource = [
          aws_opensearch_domain.vector_store.arn,
          "${aws_opensearch_domain.vector_store.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "opensearch_provider" {
  role       = aws_iam_role.opensearch_provider.name
  policy_arn = aws_iam_policy.opensearch_provider_access.arn
}

# CloudFormation実行用のIAMロール
resource "aws_iam_role" "cloudformation" {
  name = "${var.project_name}-cloudformation-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "cloudformation.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "cloudformation_admin" {
  name        = "${var.project_name}-cloudformation-admin"
  description = "Allow CloudFormation to create Bedrock resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:*",
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cloudformation" {
  role       = aws_iam_role.cloudformation.name
  policy_arn = aws_iam_policy.cloudformation_admin.arn
}