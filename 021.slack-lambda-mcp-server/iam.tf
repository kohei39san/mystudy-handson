# Bedrock が S3 にアクセスするための IAM ロール
resource "aws_iam_role" "bedrock_s3_role" {
  name = "bedrock-s3-role"

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

  tags = {
    Name    = "bedrock-s3-role"
    Project = var.project_name
  }
}

# Bedrock が S3 にアクセスするための IAM ポリシー
resource "aws_iam_policy" "bedrock_s3_policy" {
  name        = "bedrock-s3-policy"
  description = "Policy for Bedrock to access S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.data_bucket.arn,
          "${aws_s3_bucket.data_bucket.arn}/*"
        ]
      }
    ]
  })
}

# IAM ポリシーをロールにアタッチ
resource "aws_iam_role_policy_attachment" "bedrock_s3_policy_attachment" {
  role       = aws_iam_role.bedrock_s3_role.name
  policy_arn = aws_iam_policy.bedrock_s3_policy.arn
}

# Bedrock が OpenSearch にアクセスするための IAM ロール
resource "aws_iam_role" "bedrock_opensearch_role" {
  name = "bedrock-opensearch-role"

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

  tags = {
    Name    = "bedrock-opensearch-role"
    Project = var.project_name
  }
}

# Bedrock が OpenSearch にアクセスするための IAM ポリシー
resource "aws_iam_policy" "bedrock_opensearch_policy" {
  name        = "bedrock-opensearch-policy"
  description = "Policy for Bedrock to access OpenSearch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpDelete"
        ]
        Effect   = "Allow"
        Resource = [
          "${aws_opensearch_domain.kb_opensearch.arn}/*"
        ]
      }
    ]
  })
}

# IAM ポリシーをロールにアタッチ
resource "aws_iam_role_policy_attachment" "bedrock_opensearch_policy_attachment" {
  role       = aws_iam_role.bedrock_opensearch_role.name
  policy_arn = aws_iam_policy.bedrock_opensearch_policy.arn
}

# Bedrock Knowledge Base のための IAM ロール
resource "aws_iam_role" "bedrock_kb_role" {
  name = "bedrock-kb-role"

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

  tags = {
    Name    = "bedrock-kb-role"
    Project = var.project_name
  }
}

# Bedrock Knowledge Base のための IAM ポリシー
resource "aws_iam_policy" "bedrock_kb_policy" {
  name        = "bedrock-kb-policy"
  description = "Policy for Bedrock Knowledge Base"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.data_bucket.arn,
          "${aws_s3_bucket.data_bucket.arn}/*"
        ]
      },
      {
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpDelete"
        ]
        Effect   = "Allow"
        Resource = [
          "${aws_opensearch_domain.kb_opensearch.arn}/*"
        ]
      },
      {
        Action = [
          "bedrock:InvokeModel"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# IAM ポリシーをロールにアタッチ
resource "aws_iam_role_policy_attachment" "bedrock_kb_policy_attachment" {
  role       = aws_iam_role.bedrock_kb_role.name
  policy_arn = aws_iam_policy.bedrock_kb_policy.arn
}