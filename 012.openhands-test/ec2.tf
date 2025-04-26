resource "aws_instance" "example" {
  ami                    = "ami-0c55b159cbfafe1f0" # Amazon Linux 2 AMI (ap-northeast-1)
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.main.id
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  tags = {
    Name = "example-instance"
  }
}
