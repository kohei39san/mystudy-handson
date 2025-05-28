resource "aws_iam_role" "minikube_role" {
  name = "minikube_role"

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
    Name        = "minikube_role"
    Environment = var.environment
    Terraform   = "true"
  }
}

resource "aws_iam_role_policy_attachment" "minikube_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.minikube_role.name
}

resource "aws_iam_instance_profile" "minikube_instance_profile" {
  name = var.iam_instance_profile
  role = aws_iam_role.minikube_role.name

  tags = {
    Name        = "minikube_instance_profile"
    Environment = var.environment
    Terraform   = "true"
  }
}