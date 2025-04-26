resource "aws_security_group" "sg_eice" {
  name   = var.sg_eice_name
  vpc_id = aws_vpc.vpc.id
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

resource "aws_ec2_instance_connect_endpoint" "eice" {
  subnet_id          = aws_subnet.subnet.id
  security_group_ids = [aws_security_group.sg_eice.id]
}
