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
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_connect_profile.name

  network_interface {
    network_interface_id = aws_network_interface.redmine_ni.id
    device_index         = 0
  }

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp2"
  }

  user_data = file(var.user_data_path)
  tags = var.tags
  
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
}

# IAM role for EC2 Instance Connect
resource "aws_iam_role" "ec2_instance_connect_role" {
  name = "ec2-instance-connect-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# IAM policy for EC2 Instance Connect
resource "aws_iam_policy" "ec2_instance_connect_policy" {
  name        = "ec2-instance-connect-policy"
  description = "Policy for EC2 Instance Connect"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2-instance-connect:SendSSHPublicKey"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "ec2_instance_connect_attachment" {
  role       = aws_iam_role.ec2_instance_connect_role.name
  policy_arn = aws_iam_policy.ec2_instance_connect_policy.arn
}

# Instance profile for EC2 Instance Connect
resource "aws_iam_instance_profile" "ec2_instance_connect_profile" {
  name = "ec2-instance-connect-profile"
  role = aws_iam_role.ec2_instance_connect_role.name
}

# Key pair for SSH access
resource "aws_key_pair" "redmine_key" {
  key_name   = "redmine-key"
  public_key = file(var.public_key_path)
}