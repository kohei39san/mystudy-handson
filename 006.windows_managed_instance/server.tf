data "aws_ami" "windows" {
  most_recent = true
  filter {
    name   = "name"
    values = ["Windows_Server-2016-Japanese-Full-Base-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["amazon"]
}

resource "aws_network_interface" "ni" {
  subnet_id       = aws_subnet.subnet.id
  security_groups = [aws_security_group.sg.id]
}

resource "aws_instance" "instance" {
  ami                  = data.aws_ami.windows.id
  instance_type        = var.instance_type
  key_name             = aws_key_pair.kp.key_name
  iam_instance_profile = aws_iam_instance_profile.managed_node_instance_profile.name
  network_interface {
    network_interface_id = aws_network_interface.ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }
}
