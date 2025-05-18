resource "aws_security_group" "example_sg" {
  vpc_id = aws_vpc.example_vpc.id
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}