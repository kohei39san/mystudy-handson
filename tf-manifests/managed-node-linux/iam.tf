resource "aws_iam_role" "managed_node_role" {
  name = var.iam_role_name

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

resource "aws_iam_role_policy_attachment" "managed_node_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.managed_node_role.name
}

resource "aws_iam_instance_profile" "managed_node_instance_profile" {
  name = var.iam_instance_profile_name
  role = aws_iam_role.managed_node_role.name
}
