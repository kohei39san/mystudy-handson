data "aws_ssm_parameter" "ami" {
  name = var.ami_name
}
resource "aws_network_interface" "ni" {
  subnet_id       = aws_subnet.subnet.id
  security_groups = [aws_security_group.sg.id]
  
  tags = {
    Name        = "minikube_ni"
    Environment = var.environment
    Terraform   = "true"
  }
}

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = file(var.instance_public_key)
  
  tags = {
    Name        = "minikube_key_pair"
    Environment = var.environment
    Terraform   = "true"
  }
}

resource "aws_instance" "instance" {
  ami                  = data.aws_ssm_parameter.ami.value
  instance_type        = var.instance_type
  iam_instance_profile = aws_iam_instance_profile.minikube_instance_profile.name
  key_name             = aws_key_pair.deployer.key_name
  network_interface {
    network_interface_id = aws_network_interface.ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }
  
  tags = {
    Name        = "minikube_instance"
    Environment = var.environment
    Terraform   = "true"
  }
}
