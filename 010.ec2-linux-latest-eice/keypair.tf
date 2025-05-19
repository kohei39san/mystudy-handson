resource "aws_key_pair" "kp" {
  key_name   = "ec2-linux-latest-eice-key-pair"
  public_key = file(var.key_pair_public)
  
  tags = {
    Name        = "ec2-linux-latest-eice-key-pair"
    Environment = "dev"
    Terraform   = "true"
  }
}
