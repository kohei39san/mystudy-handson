resource "null_resource" "init_ec2" {
  triggers = {
    public_ip = "${module.common_resources.test_instance.public_ip}"
  }

  connection {
    type        = "ssh"
    user        = "ec2-user"
    host        = self.triggers.public_ip
    private_key = file(module.common_resources.instance_private_key)
  }

  provisioner "remote-exec" {
    script = "../../scripts/install-docker.sh"
  }
  provisioner "remote-exec" {
    script = "../../scripts/install-minikube.sh"
  }
}
