# Create SSH keys before creating the key pair
resource "null_resource" "setup_ssh" {
  provisioner "local-exec" {
    command = "bash ${path.module}/scripts/setup_ssh.sh"
  }
}

# Make aws_key_pair depend on the SSH key setup
resource "null_resource" "key_pair_dependency" {
  depends_on = [null_resource.setup_ssh]

  triggers = {
    key_pair_id = aws_key_pair.redmine_key.id
  }
}