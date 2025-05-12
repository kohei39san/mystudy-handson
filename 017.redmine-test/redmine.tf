# Find the latest Bitnami Redmine AMI
data "aws_ami" "redmine_ami" {
  most_recent = true
  owners      = ["979382823631"] # Bitnami's AWS account ID

  filter {
    name   = "name"
    values = ["bitnami-redmine-*-linux-debian-*"]
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

  # Enable EC2 Instance Connect
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  # Only use user_data if is_bitnami is true
  user_data = local.is_bitnami ? file(var.user_data_path) : null
  tags = var.tags
}

# Key pair for SSH access
resource "aws_key_pair" "redmine_key" {
  depends_on = [null_resource.setup_ssh]
  key_name   = "redmine-key"
  public_key = file(var.public_key_path)
}