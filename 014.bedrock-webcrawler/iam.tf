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

# Bedrock呼び出し用のIAMポリシー
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
          "bedrock:StartDataSourceSubsequentCrawl",
          "bedrock:GetDataSourceSubsequentCrawl"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}:*:data-source/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bedrock_invoke_attachment" {
  role       = aws_iam_role.crawler_lambda.name
  policy_arn = aws_iam_policy.bedrock_invoke_model.arn
}

# OpenSearch アクセス用のIAMポリシー
resource "aws_iam_policy" "opensearch_access" {
  name        = "${var.project_name}-opensearch-access"
  description = "Allow access to OpenSearch APIs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "OpenSearchAccessStatement"
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

resource "aws_iam_role_policy_attachment" "opensearch_access_attachment" {
  role       = aws_iam_role.crawler_lambda.name
  policy_arn = aws_iam_policy.opensearch_access.arn
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

# Bedrock用のOpenSearchアクセスポリシー
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

resource "aws_iam_role_policy_attachment" "bedrock_opensearch_attachment" {
  role       = aws_iam_role.bedrock_opensearch.name
  policy_arn = aws_iam_policy.bedrock_opensearch_access.arn
}

# OpenSearch Index作成用のIAMロール
resource "aws_iam_role" "opensearch_index_role" {
  name = "${var.project_name}-opensearch-index-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "opensearch.amazonaws.com"
        }
      },
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

# OpenSearch Index作成用のIAMポリシー
resource "aws_iam_policy" "opensearch_index_access" {
  name        = "${var.project_name}-opensearch-index-access"
  description = "Allow creating and managing OpenSearch indices"

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

resource "aws_iam_role_policy_attachment" "opensearch_index_attachment" {
  role       = aws_iam_role.opensearch_index_role.name
  policy_arn = aws_iam_policy.opensearch_index_access.arn
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

# CloudFormation用のIAMポリシー（最小権限に制限）
resource "aws_iam_policy" "cloudformation_policy" {
  name        = "${var.project_name}-cloudformation-policy"
  description = "Allow CloudFormation to create Bedrock resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:CreateKnowledgeBase",
          "bedrock:DeleteKnowledgeBase",
          "bedrock:GetKnowledgeBase",
          "bedrock:UpdateKnowledgeBase",
          "bedrock:CreateDataSource",
          "bedrock:DeleteDataSource",
          "bedrock:GetDataSource",
          "bedrock:UpdateDataSource"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}:*:knowledge-base/*",
          "arn:aws:bedrock:${var.aws_region}:*:data-source/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.bedrock_opensearch.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cloudformation_attachment" {
  role       = aws_iam_role.cloudformation.name
  policy_arn = aws_iam_policy.cloudformation_policy.arn
}

# 現在のAWSアカウントIDを取得
data "aws_caller_identity" "current" {}