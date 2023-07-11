resource "docker_image" "myflask" {
  name = "myflask"
  build {
    context = "../container-images"
    tag     = ["myflask:v1.0"]
  }
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset(path.module, "../container-images") : filesha1(f)]))
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
