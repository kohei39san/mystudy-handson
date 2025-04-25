# https://docs.aws.amazon.com/bedrock/latest/userguide/kb-permissions.html
resource "aws_iam_role" "bedrock_knowledge_base" {
  name = "bedrock-knowledge-base-role"

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

# https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html
resource "aws_iam_policy" "opensearch_access" {
  name        = "bedrock-opensearch-access"
  description = "Permissions for Bedrock to access OpenSearch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpGet",
          "es:ESHead"
        ]
        Resource = "${aws_opensearch_domain.knowledge_base.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "opensearch_access" {
  role       = aws_iam_role.bedrock_knowledge_base.name
  policy_arn = aws_iam_policy.opensearch_access.arn
}
