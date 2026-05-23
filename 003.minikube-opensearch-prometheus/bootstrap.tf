resource "terraform_data" "bootstrap" {
  triggers_replace = [
    aws_instance.instance.id,
  ]

  connection {
    type        = "ssh"
    user        = "ec2-user"
    host        = aws_instance.instance.public_ip
    private_key = file(var.instance_private_key)
  }
  provisioner "remote-exec" {
    script = "./scripts/install-docker.sh"
  }
  provisioner "remote-exec" {
    script = "./scripts/install-minikube.sh"
  }
}