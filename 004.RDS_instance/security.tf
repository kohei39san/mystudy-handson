resource "aws_security_group" "example_sg" {
  vpc_id = aws_vpc.example_vpc.id

  tags = {
    Name        = "rds-sg"
    Environment = var.environment
    Terraform   = "true"
  }
}