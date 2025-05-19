resource "aws_key_pair" "test_kp" {
  public_key = file(var.instance_public_key)
  
  tags = {
    Name        = "test_kp"
    Environment = var.environment
    Terraform   = "true"
  }
}
