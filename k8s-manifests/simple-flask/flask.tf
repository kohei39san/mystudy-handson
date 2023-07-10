resource "docker_image" "myflask" {
  name = "myflask"
  build {
    context = "../container-images"
    tag     = ["myflask:v1.0"]
  }
}

module "myflask" {
  source  = "kbst.xyz/catalog/custom-manifests/kustomization"
  version = "0.4.0"

  configuration_base_key = "default"

  configuration = {
    default = {
      namespace = "default"
      resources = [
        "kustomize/flask.yaml",
      ]
      secret_generator = [{
        name = "myflask"
        envs = [
          ".pgpass"
        ]
      }]
    }
  }

}
