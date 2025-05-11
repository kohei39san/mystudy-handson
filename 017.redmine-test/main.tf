

# Key pair for SSH access
resource "aws_key_pair" "redmine_key" {
  key_name   = "redmine-key"
  public_key = file(var.public_key_path)
}