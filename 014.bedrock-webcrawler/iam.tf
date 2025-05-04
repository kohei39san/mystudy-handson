# 既存のLambda用IAMロール
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

resource "aws_iam_role_policy" "bedrock_invoke_model" {
  name = "bedrock-invoke-model"
  role = aws_iam_role.crawler_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvokeModelStatement"
        Effect = "Allow"
        Action = [
          "bedrock:*"
        ]
        Resource = [
          "*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "opensearch_access" {
  name = "opensearch-api-access"
  role = aws_iam_role.crawler_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "OpenSearchServerlessAPIAccessAllStatement"
        Effect = "Allow"
        Action = [
          "aoss:APIAccessAll"
        ]
        Resource = [
          "*"
        ]
      }
    ]
  })
}

# BedrockとOpenSearchの連携用のIAMロール（新規追加）
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

resource "aws_iam_role_policy" "bedrock_opensearch_access" {
  name = "bedrock-opensearch-access"
  role = aws_iam_role.bedrock_opensearch.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "aoss:APIAccessAll",
          "es:DescribeDomain"
        ]
        Resource = [aws_opensearch_domain.vector_store.arn]
      }
    ]
  })
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

resource "aws_iam_role_policy_attachment" "cloudformation" {
  role       = aws_iam_role.cloudformation.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}