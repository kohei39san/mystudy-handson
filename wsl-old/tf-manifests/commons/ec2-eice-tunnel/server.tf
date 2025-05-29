# tflint-ignore-file: terraform_required_providers
data "aws_ssm_parameter" "ami" {
  name = var.ami_name
}
resource "aws_network_interface" "ni" {
  subnet_id       = aws_subnet.subnet.id
  security_groups = [aws_security_group.sg.id]
}

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = file(var.instance_public_key)
}

# Add IAM role and instance profile
resource "aws_iam_role" "eice_tunnel_role" {
  name = "eice-tunnel-role"

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

resource "aws_iam_role_policy_attachment" "eice_tunnel_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.eice_tunnel_role.name
}

resource "aws_iam_instance_profile" "eice_tunnel_instance_profile" {
  name = var.iam_instance_profile
  role = aws_iam_role.eice_tunnel_role.name
}

resource "aws_instance" "instance" {
  ami                  = data.aws_ssm_parameter.ami.value
  instance_type        = var.instance_type
  iam_instance_profile = aws_iam_instance_profile.eice_tunnel_instance_profile.name
  key_name             = aws_key_pair.deployer.key_name
  network_interface {
    network_interface_id = aws_network_interface.ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }
}
