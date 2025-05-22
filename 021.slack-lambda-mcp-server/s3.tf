# データソース用のS3バケット
resource "aws_s3_bucket" "data_bucket" {
  bucket = var.s3_bucket_name
  
  tags = {
    Name        = var.s3_bucket_name
    Environment = "production"
    Project     = var.project_name
  }
}

# S3バケットのパブリックアクセスをブロック
resource "aws_s3_bucket_public_access_block" "data_bucket_access_block" {
  bucket = aws_s3_bucket.data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3バケットのサーバーサイド暗号化を有効化
resource "aws_s3_bucket_server_side_encryption_configuration" "data_bucket_encryption" {
  bucket = aws_s3_bucket.data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3バケットのライフサイクルルール
resource "aws_s3_bucket_lifecycle_configuration" "data_bucket_lifecycle" {
  bucket = aws_s3_bucket.data_bucket.id

  rule {
    id     = "archive-old-objects"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 180
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

# BedrockがナレッジベースのデータソースとしてアクセスするためのS3バケットポリシー
resource "aws_s3_bucket_policy" "data_bucket_policy" {
  bucket = aws_s3_bucket.data_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowBedrockAccess"
        Effect    = "Allow"
        Principal = {
          AWS = aws_iam_role.bedrock_s3_role.arn
        }
        Action    = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource  = [
          aws_s3_bucket.data_bucket.arn,
          "${aws_s3_bucket.data_bucket.arn}/*"
        ]
      }
    ]
  })
}