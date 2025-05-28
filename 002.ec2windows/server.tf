resource "aws_network_interface" "test_ni" {
  subnet_id       = aws_subnet.test_subnet.id
  security_groups = concat([aws_security_group.test_sg.id], var.vpc_security_group_ids)
  private_ips     = ["10.0.0.10"]

  tags = {
    Name        = "test_ni"
    Environment = var.environment
    Terraform   = "true"
  }
}

# Get the latest Windows Server 2019 AMI
data "aws_ami" "windows" {
  most_recent = true
  filter {
    name   = "name"
    values = ["Windows_Server-2019-English-Full-Base-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["801119661308"] # Amazon
}

resource "aws_instance" "test_instance" {
  ami           = var.ami_id != "" ? var.ami_id : data.aws_ami.windows.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.test_kp.id
  network_interface {
    network_interface_id = aws_network_interface.test_ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }

  tags = {
    Name        = "test_instance"
    Environment = var.environment
    Terraform   = "true"
  }
}
