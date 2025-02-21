resource "aws_key_pair" "kp" {
  key_name   = var.key_pair
  public_key = file(var.key_pair_public)
}
