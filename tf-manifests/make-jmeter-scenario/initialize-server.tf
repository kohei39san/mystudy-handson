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

  provisioner "file" {
    source      = "../../scripts/git-clone.sh"
    destination = "/tmp/git-clone.sh"
  }
  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/git-clone.sh",
      "COMMIT_ID=${var.commit_id} REPO_URL=${var.repo_url} /tmp/git-clone.sh",
    ]
  }
  provisioner "remote-exec" {
    inline = [
      "/tmp/mystudy-handson/scripts/install-docker.sh",
    ]
  }
  provisioner "remote-exec" {
    inline = [
      "KUBE_VERSION=${var.kube_version} /tmp/mystudy-handson/scripts/install-minikube.sh",
    ]
  }
  provisioner "remote-exec" {
    inline = [
      "JMETER_VERSION=${var.jmeter_version} /tmp/mystudy-handson/scripts/install-jmeter.sh",
      "/tmp/mystudy-handson/scripts/install-terraform.sh",
    ]
  }
}
