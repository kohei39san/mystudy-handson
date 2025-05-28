resource "aws_key_pair" "kp" {
  key_name   = var.key_pair
  public_key = file(var.key_pair_public)

  tags = merge(var.aws_tags, {
    Name = "managed_node_linux_key_pair"
  })
}
