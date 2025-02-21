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
resource "aws_security_group" "sg" {
  name   = var.sg_name
  vpc_id = aws_vpc.vpc.id
}
resource "aws_security_group" "sg_eice" {
  name   = var.sg_eice_name
  vpc_id = aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "sg_egress" {
  security_group_id = aws_security_group.sg.id

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  from_port   = 0
  to_port     = 0
}

resource "aws_vpc_security_group_ingress_rule" "sg_ingress" {
  security_group_id = aws_security_group.sg.id

  referenced_security_group_id = aws_security_group.sg_eice.id
  ip_protocol                  = "tcp"
  from_port                    = 22
  to_port                      = 22
}

resource "aws_vpc_security_group_egress_rule" "sg_eice_egress" {
  security_group_id = aws_security_group.sg_eice.id

  referenced_security_group_id = aws_security_group.sg.id
  ip_protocol                  = "tcp"
  from_port                    = 22
  to_port                      = 22
}
