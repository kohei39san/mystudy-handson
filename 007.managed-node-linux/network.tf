data "http" "client_global_ip" {
  url = "https://ifconfig.co/ip"
}

locals {
  allowed_cidr = replace("${data.http.client_global_ip.response_body}/32", "\n", "")
}

resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_cidr_block

  tags = {
    Name = "managed_node_linux_vpc"
  }
}
resource "aws_subnet" "subnet" {
  vpc_id                  = aws_vpc.vpc.id
  map_public_ip_on_launch = true
  cidr_block              = var.subnet_cidr_block

  tags = {
    Name = "managed_node_linux_subnet"
  }
}
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "managed_node_linux_igw"
  }
}
resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "managed_node_linux_rt"
  }
}
resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.rt.id

  # Tags are not supported for aws_route_table_association
}

resource "aws_security_group" "sg" {
  name   = "sg"
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "managed_node_linux_sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "sg_ingress" {
  security_group_id = aws_security_group.sg.id

  cidr_ipv4   = local.allowed_cidr
  ip_protocol = "tcp"
  from_port   = "22"
  to_port     = "22"

  tags = {
    Name = "managed_node_linux_sg_ingress"
  }
}

resource "aws_vpc_security_group_egress_rule" "sg_egress" {
  security_group_id = aws_security_group.sg.id

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  from_port   = "-1"
  to_port     = "-1"

  tags = {
    Name = "managed_node_linux_sg_egress"
  }
}