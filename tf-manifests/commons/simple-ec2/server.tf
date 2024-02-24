data "aws_ssm_parameter" "ami" {
  name = var.ami_name
}
resource "aws_network_interface" "test_ni" {
  subnet_id       = aws_subnet.test_subnet.id
  security_groups = concat([aws_security_group.test_sg.id], var.vpc_security_group_ids)
}
resource "aws_instance" "test_instance" {
  ami           = data.aws_ssm_parameter.ami.value
  instance_type = var.instance_type
  key_name      = aws_key_pair.test_kp.id
  network_interface {
    network_interface_id = aws_network_interface.test_ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }
}
