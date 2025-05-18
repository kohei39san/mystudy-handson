data "aws_ssm_parameter" "ami" {
  name = var.ami_name
}
resource "aws_network_interface" "ni" {
  subnet_id       = aws_subnet.subnet.id
  security_groups = [aws_security_group.sg.id]
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = file(var.instance_public_key)
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}

resource "aws_instance" "instance" {
  ami                  = data.aws_ssm_parameter.ami.value
  instance_type        = var.instance_type
  key_name             = aws_key_pair.deployer.key_name
  network_interface {
    network_interface_id = aws_network_interface.ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}
