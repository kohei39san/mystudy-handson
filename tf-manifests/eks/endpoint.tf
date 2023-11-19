resource "aws_ec2_instance_connect_endpoint" "eice" {
  subnet_id          = aws_subnet.kubectl_subnet.id
  security_group_ids = [aws_security_group.kubectl_sg.id]
}

data "aws_ssm_parameter" "ami" {
  name = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
}

resource "aws_network_interface" "kubectl_ni" {
  subnet_id       = aws_subnet.kubectl_subnet.id
  security_groups = [aws_security_group.kubectl_sg.id]
}

resource "aws_iam_instance_profile" "kubectl_iam_instance_profile" {
  name = var.instance_iam_instance_profile_name
  role = aws_iam_role.kubectl_role.name
}

resource "aws_instance" "kubectl_instance" {
  ami                  = data.aws_ssm_parameter.ami.value
  instance_type        = var.instance_type
  iam_instance_profile = aws_iam_instance_profile.kubectl_iam_instance_profile.name
  network_interface {
    network_interface_id = aws_network_interface.kubectl_ni.id
    device_index         = 0
  }
}
