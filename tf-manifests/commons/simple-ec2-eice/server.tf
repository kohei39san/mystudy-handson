data "aws_ssm_parameter" "ami" {
  name = var.ami_name
}
resource "aws_network_interface" "ni" {
  subnet_id       = aws_subnet.subnet.id
}
resource "aws_instance" "instance" {
  ami           = data.aws_ssm_parameter.ami.value
  instance_type = var.instance_type
  network_interface {
    network_interface_id = aws_network_interface.ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }
}
