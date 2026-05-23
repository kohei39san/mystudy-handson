resource "aws_vpc" "example_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name        = "rds-vpc"
    Environment = var.environment
    Terraform   = "true"
  }
}

resource "aws_subnet" "example_subnet1" {
  vpc_id            = aws_vpc.example_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "ap-northeast-1c"

  tags = {
    Name        = "rds-subnet-1"
    Environment = var.environment
    Terraform   = "true"
  }
}

resource "aws_subnet" "example_subnet2" {
  vpc_id            = aws_vpc.example_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "ap-northeast-1a"

  tags = {
    Name        = "rds-subnet-2"
    Environment = var.environment
    Terraform   = "true"
  }
}