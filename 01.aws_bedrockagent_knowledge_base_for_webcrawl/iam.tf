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

resource "aws_iam_role_policy" "bedrock_os_access" {
  name = "bedrock-os-access-policy"
  role = aws_iam_role.bedrock_knowledge_base.name

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
        Resource = [
          "${aws_opensearch_domain.knowledge_base.arn}/*",
          "${aws_opensearch_domain.knowledge_base.arn}"
        ]
      }
    ]
  })
}
