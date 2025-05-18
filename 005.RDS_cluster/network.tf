resource "aws_vpc" "example_vpc" {
  cidr_block = "10.0.0.0/16"
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}

resource "aws_subnet" "example_subnet1" {
  vpc_id            = aws_vpc.example_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "ap-northeast-1c"
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}

resource "aws_subnet" "example_subnet2" {
  vpc_id            = aws_vpc.example_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "ap-northeast-1a"
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}