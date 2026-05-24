resource "aws_network_interface" "ni" {
  subnet_id       = aws_subnet.subnet.id
  security_groups = [aws_security_group.sg.id]
}

# Get the latest Windows Server AMI
data "aws_ami" "windows_latest" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["Windows_Server-2022-English-Full-Base-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "instance" {
  ami                  = var.ami != "" ? var.ami : data.aws_ami.windows_latest.id
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
