module "git_clone" {
  source      = "../commons/eice-remote-exec"
  instance_id = module.common_resources.instance.id
  public_ip   = module.common_resources.instance.public_ip
  scripts     = ["../../scripts/git-clone.sh"]
  environment = {
    COMMIT_ID = "feature/grafana-alert"
  }
}

module "install_minikube" {
  source      = "../commons/eice-remote-exec"
  instance_id = module.common_resources.instance.id
  public_ip   = module.common_resources.instance.public_ip
  inline     = ["/tmp/mystudy-handson/scripts/install-minikube.sh"]
}
