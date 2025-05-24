data "http" "client_global_ip" {
  url = "https://inet-ip.info/ip"
}
locals {
  allowed_cidr = "${data.http.client_global_ip.response_body}/32"
}

resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_cidr_block

  tags = {
    Name        = "minikube_vpc"
    Environment = var.environment
    Terraform   = "true"
  }
}
resource "aws_subnet" "subnet" {
  vpc_id                  = aws_vpc.vpc.id
  map_public_ip_on_launch = true
  cidr_block              = var.subnet_cidr_block

  tags = {
    Name        = "minikube_subnet"
    Environment = var.environment
    Terraform   = "true"
  }
}
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name        = "minikube_igw"
    Environment = var.environment
    Terraform   = "true"
  }
}
resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name        = "minikube_rt"
    Environment = var.environment
    Terraform   = "true"
  }
}
resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.rt.id
}
resource "aws_security_group" "sg" {
  name   = var.sg_name
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name        = "minikube_sg"
    Environment = var.environment
    Terraform   = "true"
  }
}

resource "aws_vpc_security_group_egress_rule" "sg_egress" {
  security_group_id = aws_security_group.sg.id

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  from_port   = -1
  to_port     = -1

  tags = {
    Name        = "minikube_sg_egress"
    Environment = var.environment
    Terraform   = "true"
  }
}

resource "aws_vpc_security_group_ingress_rule" "sg_ingress" {
  security_group_id = aws_security_group.sg.id

  cidr_ipv4   = local.allowed_cidr
  ip_protocol = "tcp"
  from_port   = 22
  to_port     = 22

  tags = {
    Name        = "minikube_sg_ingress"
    Environment = var.environment
    Terraform   = "true"
  }
}
