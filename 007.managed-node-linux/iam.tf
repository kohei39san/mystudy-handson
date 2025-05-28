resource "aws_iam_role" "managed_node_role" {
  name = "managed_node_linux_role"

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
  
  tags = {
    Name = "managed_node_linux_role"
  }
}

resource "aws_iam_role_policy_attachment" "managed_node_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.managed_node_role.name
  
  # Tags are not supported for aws_iam_role_policy_attachment
}

resource "aws_iam_instance_profile" "managed_node_instance_profile" {
  name = var.iam_instance_profile
  role = aws_iam_role.managed_node_role.name
  
  tags = {
    Name = "managed_node_linux_instance_profile"
  }
}
