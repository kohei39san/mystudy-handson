# VPC
resource "aws_vpc" "redmine_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = var.tags
}

# Public subnet
resource "aws_subnet" "redmine_subnet" {
  vpc_id                  = aws_vpc.redmine_vpc.id
  cidr_block              = var.subnet_cidr
  map_public_ip_on_launch = true
  tags                    = var.tags
}

# Internet Gateway
resource "aws_internet_gateway" "redmine_igw" {
  vpc_id = aws_vpc.redmine_vpc.id
  tags   = var.tags
}

# Route table
resource "aws_route_table" "redmine_rt" {
  vpc_id = aws_vpc.redmine_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.redmine_igw.id
  }

  tags = var.tags
}

# Route table association
resource "aws_route_table_association" "redmine_rta" {
  subnet_id      = aws_subnet.redmine_subnet.id
  route_table_id = aws_route_table.redmine_rt.id
}

# Security group
resource "aws_security_group" "redmine_sg" {
  name        = var.security_group_name
  description = "Security group for Redmine server"
  vpc_id      = aws_vpc.redmine_vpc.id

  tags = var.tags
}

resource "aws_vpc_security_group_ingress_rule" "redmine_sg_ingress80" {
  security_group_id = aws_security_group.redmine_sg.id

  cidr_ipv4   = var.allowed_ip
  ip_protocol = "tcp"
  from_port   = 80
  to_port     = 80
}

resource "aws_vpc_security_group_ingress_rule" "redmine_sg_ingress443" {
  security_group_id = aws_security_group.redmine_sg.id

  cidr_ipv4   = var.allowed_ip
  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443
}

resource "aws_vpc_security_group_egress_rule" "redmine_sg_egress" {
  security_group_id = aws_security_group.redmine_sg.id

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  from_port   = 0
  to_port     = 0
}