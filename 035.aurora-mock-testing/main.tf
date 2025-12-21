# IAM role for RDS IAM token authentication
resource "aws_iam_role" "rds_iam_role" {
  name = "${var.project_name}-${var.environment}-rds-iam-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "lambda.amazonaws.com",
            "ecs-tasks.amazonaws.com"
          ]
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-iam-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM policy for RDS connect
resource "aws_iam_policy" "rds_connect_policy" {
  name        = "${var.project_name}-${var.environment}-rds-connect-policy"
  description = "Policy for RDS IAM token authentication"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = [
          "arn:aws:rds-db:${var.aws_region}:*:dbuser:*/${var.db_username}"
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-connect-policy"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "rds_connect_policy_attachment" {
  role       = aws_iam_role.rds_iam_role.name
  policy_arn = aws_iam_policy.rds_connect_policy.arn
}

# IAM user for PostgreSQL IAM token authentication
resource "aws_iam_user" "postgres_iam_user" {
  name = "${var.project_name}-${var.environment}-postgres-iam-user"
  path = "/"

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres-iam-user"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM policy for the PostgreSQL user
resource "aws_iam_user_policy" "postgres_iam_user_policy" {
  name = "${var.project_name}-${var.environment}-postgres-iam-user-policy"
  user = aws_iam_user.postgres_iam_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = [
          "arn:aws:rds-db:${var.aws_region}:*:dbuser:*/${var.db_username}"
        ]
      }
    ]
  })
}

# Data source for current AWS account ID
data "aws_caller_identity" "current" {}

# Data source for current AWS region
data "aws_region" "current" {}