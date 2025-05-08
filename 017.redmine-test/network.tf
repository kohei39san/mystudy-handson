resource "aws_vpc" "redmine_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_subnet" "redmine_subnet" {
  vpc_id                  = aws_vpc.redmine_vpc.id
  cidr_block              = var.subnet_cidr
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"
}

resource "aws_internet_gateway" "redmine_igw" {
  vpc_id = aws_vpc.redmine_vpc.id
}

resource "aws_route_table" "redmine_rt" {
  vpc_id = aws_vpc.redmine_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.redmine_igw.id
  }
}

resource "aws_route_table_association" "redmine_rta" {
  subnet_id      = aws_subnet.redmine_subnet.id
  route_table_id = aws_route_table.redmine_rt.id
}

resource "aws_security_group" "redmine_sg" {
  name        = "redmine-security-group"
  description = "Security group for Redmine instance"
  vpc_id      = aws_vpc.redmine_vpc.id

  # SSH access from allowed IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ip]
    description = "SSH access from allowed IP"
  }

  # HTTP access from allowed IP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ip]
    description = "HTTP access from allowed IP"
  }

  # HTTPS access from allowed IP
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ip]
    description = "HTTPS access from allowed IP"
  }

  # Outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
}