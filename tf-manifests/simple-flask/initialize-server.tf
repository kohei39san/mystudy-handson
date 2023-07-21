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
  provisioner "remote-exec" {
    script = "../../scripts/install-helm.sh"
  }

  provisioner "file" {
    source      = "../../k8s-manifests/simple-flask"
    destination = "/tmp/k8s-manifests"
  }

  provisioner "file" {
    source      = "../../container-images/simple-flask"
    destination = "/tmp/container-images"
  }

  provisioner "remote-exec" {
    script = "../../scripts/install-for-simple-flask.sh"
  }
}
