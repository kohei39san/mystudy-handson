module "git_clone" {
  source      = "../commons/eice-remote-exec"
  instance_id = module.common_resources.instance.id
  public_ip   = module.common_resources.instance.public_ip
  scripts     = ["../../scripts/git-clone.sh"]
  environment = {
    COMMIT_ID = "feature/grafana-alert"
  }
}

module "install_docker" {
  source            = "../commons/eice-remote-exec"
  instance_id       = module.common_resources.instance.id
  public_ip         = module.common_resources.instance.public_ip
  depends_on_cmd_id = module.git_clone.id
  inline = [
    "/tmp/mystudy-handson/scripts/install-docker.sh",
  ]
}

module "install_minikube" {
  source            = "../commons/eice-remote-exec"
  instance_id       = module.common_resources.instance.id
  public_ip         = module.common_resources.instance.public_ip
  depends_on_cmd_id = module.install_docker.id
  inline = [
    "/tmp/mystudy-handson/scripts/install-minikube.sh",
  ]
}
