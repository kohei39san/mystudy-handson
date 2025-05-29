# tflint-ignore-file: terraform_required_providers
data "aws_ssm_parameter" "ami" {
  name = var.ami_name
}
resource "aws_network_interface" "ni" {
  subnet_id       = aws_subnet.subnet.id
  security_groups = var.vpc_security_group_ids
}

# Add key pair resource
resource "aws_key_pair" "simple_ec2_key" {
  key_name   = var.key_pair
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD3F6tyPEFEzV0LX3X8BsXdMsQz1x2cEikKDEY0aIj41qgxMCP/iteneqXSIFZBp5vizPvaoIR3Um9xK7PGoW8giupGn+EPuxIA4cDM4vzOqOkiMPhz5XK0whEjkVzTo4+S0puvDZuwIsdiW9mxhJc7tgBNL0cYlWSYVkz4G/fslNfRPW5mYAM49f4fhtxPb5ok4Q2Lg9dPKVHO/Bgeu5woMc7RY0p1ej6D4CKFE6lymSDJpW0YHX/wqE9+cfEauh7xZcG0q9t2ta6F6fmX0agvpFyZo8aFbXeUBr7osSCJNgvavWbM/06niWrOvYX2xwWdhXmXSrbX8ZbabVohBK41 example@example.com"
}

# Add IAM role and instance profile
resource "aws_iam_role" "simple_ec2_role" {
  name = "simple-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "simple_ec2_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.simple_ec2_role.name
}

resource "aws_iam_instance_profile" "simple_ec2_instance_profile" {
  name = var.iam_instance_profile
  role = aws_iam_role.simple_ec2_role.name
}

resource "aws_instance" "instance" {
  ami                  = data.aws_ssm_parameter.ami.value
  instance_type        = var.instance_type
  key_name             = aws_key_pair.simple_ec2_key.key_name
  iam_instance_profile = aws_iam_instance_profile.simple_ec2_instance_profile.name
  network_interface {
    network_interface_id = aws_network_interface.ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }
}
