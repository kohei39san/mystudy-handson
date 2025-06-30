# tflint-ignore-file: terraform_required_providers
resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_cidr_block
}
resource "aws_subnet" "subnet" {
  vpc_id                  = aws_vpc.vpc.id
  map_public_ip_on_launch = true
  cidr_block              = var.subnet_cidr_block
}
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
}
resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}
resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.rt.id
}
