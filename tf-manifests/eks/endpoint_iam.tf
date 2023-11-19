resource "aws_iam_policy" "kubectl_policy" {
  name        = "test_kubectl_policy"
  description = "test kubectl policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sts:GetCallerIdentity",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role" "kubectl_role" {
  name = "test_kubectl_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "kubectl_iam_role_policy_attachment" {
  policy_arn = aws_iam_policy.kubectl_policy.arn
  role       = aws_iam_role.kubectl_role.name
}
