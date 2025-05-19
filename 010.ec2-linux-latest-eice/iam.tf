resource "aws_iam_role" "managed_node_role" {
  name = "managed_node_role"

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
    Name        = "managed_node_role"
    Environment = "dev"
    Terraform   = "true"
  }
}

resource "aws_iam_role_policy_attachment" "managed_node_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.managed_node_role.name
}

resource "aws_iam_instance_profile" "managed_node_instance_profile" {
  name = "ec2-linux-latest-eice-instance-profile"
  role = aws_iam_role.managed_node_role.name
  
  tags = {
    Name        = "managed_node_instance_profile"
    Environment = "dev"
    Terraform   = "true"
  }
}
