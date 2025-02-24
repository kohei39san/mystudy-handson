module "git_clone" {
  source      = "../commons/eice-remote-exec"
  instance_id = module.common_resources.instance.id
  public_ip   = module.common_resources.instance.public_ip
  scripts     = ["../../scripts/git-clone.sh"]
  environment = {
    COMMIT_ID = "feature/grafana-alert"
    CLONE_DIR = "/tmp"
  }
}

module "install_docker" {
  source         = "../commons/eice-remote-exec"
  instance_id    = module.common_resources.instance.id
  public_ip      = module.common_resources.instance.public_ip
  depends_on_cmd = module.git_clone.id
  inline = [
    "/tmp/mystudy-handson/scripts/install-docker.sh",
  ]
  environment = {
    DOCKER_VERSION = "24.0.5"
  }
}

module "install_kubernetes" {
  source         = "../commons/eice-remote-exec"
  instance_id    = module.common_resources.instance.id
  public_ip      = module.common_resources.instance.public_ip
  depends_on_cmd = module.install_docker.id
  inline = [
    "/tmp/mystudy-handson/scripts/install-minikube-bare-metal.sh",
    "/tmp/mystudy-handson/scripts/install-terraform.sh",
  ]
}

module "apply_prometheus_operator" {
  source         = "../commons/eice-remote-exec"
  instance_id    = module.common_resources.instance.id
  public_ip      = module.common_resources.instance.public_ip
  depends_on_cmd = module.install_kubernetes.id
  inline = [
    "/tmp/mystudy-handson/scripts/terraform-apply.sh",
  ]
  environment = {
    TF_DIR = "/tmp/mystudy-handson/k8s-manifests/prometheus-operator/"
  }
}
