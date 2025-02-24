data "http" "client_global_ip" {
  url = "https://ifconfig.co/ip"
}

locals {
  allowed_cidr = replace("${data.http.client_global_ip.response_body}/32", "\n", "")
}

resource "aws_security_group" "sg" {
  name   = var.sg_name
  vpc_id = module.common.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "sg_ingress" {
  security_group_id = aws_security_group.sg.id

  cidr_ipv4   = local.allowed_cidr
  ip_protocol = "tcp"
  from_port   = var.rdp_port
  to_port     = var.rdp_port
}

resource "aws_vpc_security_group_egress_rule" "sg_egress" {
  security_group_id = aws_security_group.sg.id

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  from_port   = 0
  to_port     = 0
}
