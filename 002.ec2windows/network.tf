data "http" "client_global_ip" {
  url = "http://ipv4.icanhazip.com/"
}
locals {
  allowed_cidr = replace("${data.http.client_global_ip.response_body}/32", "\n", "")
}
resource "aws_vpc" "test_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name        = "test_vpc"
    Environment = var.environment
    Terraform   = "true"
  }
}
resource "aws_subnet" "test_subnet" {
  vpc_id                  = aws_vpc.test_vpc.id
  map_public_ip_on_launch = true
  cidr_block              = "10.0.0.0/24"

  tags = {
    Name        = "test_subnet"
    Environment = var.environment
    Terraform   = "true"
  }
}
resource "aws_internet_gateway" "test_igw" {
  vpc_id = aws_vpc.test_vpc.id

  tags = {
    Name        = "test_igw"
    Environment = var.environment
    Terraform   = "true"
  }
}
resource "aws_route_table" "test_rt" {
  vpc_id = aws_vpc.test_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.test_igw.id
  }

  tags = {
    Name        = "test_rt"
    Environment = var.environment
    Terraform   = "true"
  }
}
resource "aws_route_table_association" "test_rta" {
  subnet_id      = aws_subnet.test_subnet.id
  route_table_id = aws_route_table.test_rt.id
}
resource "aws_security_group" "test_sg" {
  vpc_id = aws_vpc.test_vpc.id
  ingress {
    from_port   = 0
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = [local.allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "test_sg"
    Environment = var.environment
    Terraform   = "true"
  }
}
