locals {
  private_server_ip = "${aws_instance.test_instance.private_ip}/32"
}

resource "aws_security_group" "private_server_sg" {
  vpc_id = aws_vpc.test_vpc.id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.private_server_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_subnet" "private_server_subnet" {
  vpc_id                  = aws_vpc.test_vpc.id
  map_public_ip_on_launch = true
  cidr_block              = "10.0.1.0/24"
}

resource "aws_route_table_association" "private_server_rta" {
  subnet_id      = aws_subnet.private_server_subnet.id
  route_table_id = aws_route_table.test_rt.id
}

resource "aws_network_interface" "private_server_ni" {
  subnet_id       = aws_subnet.private_server_subnet.id
  security_groups = [aws_security_group.private_server_sg.id, aws_security_group.test_sg.id]
  private_ips     = ["10.0.1.10"]
}
resource "aws_instance" "private_server" {
  ami           = data.aws_ssm_parameter.ami.value
  instance_type = var.instance_type
  key_name      = aws_key_pair.test_kp.id
  network_interface {
    network_interface_id = aws_network_interface.private_server_ni.id
    device_index         = 0
  }
  root_block_device {
    volume_size = var.root_block_volume_size
  }
}

resource "terraform_data" "private_server_bootstrap" {
  triggers_replace = [
    aws_instance.private_server.id,
  ]

  connection {
    type        = "ssh"
    user        = "ec2-user"
    host        = aws_instance.private_server.public_ip
    private_key = file(var.instance_private_key)
  }
  provisioner "remote-exec" {
    script = "../scripts/001.ec2-ec2,ec2/bootstrap.sh"
  }
}