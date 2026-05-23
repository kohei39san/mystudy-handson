resource "terraform_data" "bootstrap" {
  triggers_replace = [
    aws_instance.test_instance.id,
  ]

  connection {
    type        = "ssh"
    user        = "ec2-user"
    host        = aws_instance.test_instance.public_ip
    private_key = file(var.instance_private_key)
  }
  provisioner "remote-exec" {
    script = "./scripts/bootstrap.sh"
  }
}