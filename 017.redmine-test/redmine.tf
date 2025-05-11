# Find the latest Amazon Linux 2 AMI
data "aws_ami" "redmine_ami" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Create network interface
resource "aws_network_interface" "redmine_ni" {
  subnet_id       = aws_subnet.redmine_subnet.id
  security_groups = [aws_security_group.redmine_sg.id]
}

# Create EC2 instance
resource "aws_instance" "redmine_instance" {
  ami           = data.aws_ami.redmine_ami.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.redmine_key.key_name

  network_interface {
    network_interface_id = aws_network_interface.redmine_ni.id
    device_index         = 0
  }

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp2"
  }

volume_type = "gp2"
  }

  user_data = file(var.user_data_path)

  tags = var.tags
}

  tags = var.tags
}