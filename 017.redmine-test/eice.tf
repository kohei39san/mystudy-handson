resource "aws_security_group" "sg_eice" {
  name   = var.sg_eice_name
  vpc_id = aws_vpc.redmine_vpc.id
  
  tags = {
    Name        = var.sg_eice_name
    Environment = var.tags["Environment"]
    Terraform   = "true"
  }
}

resource "aws_vpc_security_group_ingress_rule" "sg_ingress" {
  security_group_id = aws_security_group.redmine_sg.id

  referenced_security_group_id = aws_security_group.sg_eice.id
  ip_protocol                  = "tcp"
  from_port                    = 22
  to_port                      = 22
  
  tags = {
    Name        = "redmine-sg-ingress"
    Environment = var.tags["Environment"]
    Terraform   = "true"
  }
}

resource "aws_vpc_security_group_egress_rule" "sg_eice_egress" {
  security_group_id = aws_security_group.sg_eice.id

  referenced_security_group_id = aws_security_group.redmine_sg.id
  ip_protocol                  = "tcp"
  from_port                    = 22
  to_port                      = 22
  
  tags = {
    Name        = "redmine-sg-eice-egress"
    Environment = var.tags["Environment"]
    Terraform   = "true"
  }
}

resource "aws_ec2_instance_connect_endpoint" "eice" {
  subnet_id          = aws_subnet.redmine_subnet.id
  security_group_ids = [aws_security_group.sg_eice.id]
  
  tags = {
    Name        = "redmine-eice"
    Environment = var.tags["Environment"]
    Terraform   = "true"
  }
}
