resource "aws_key_pair" "test_kp" {
  public_key = file(var.instance_public_key)
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}
