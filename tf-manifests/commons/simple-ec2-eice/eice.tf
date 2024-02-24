resource "aws_ec2_instance_connect_endpoint" "eice" {
  subnet_id          = aws_subnet.subnet.id
  security_group_ids = [aws_security_group.sg.id]
}
