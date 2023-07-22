resource "docker_image" "myflask" {
  name = "myflask"
  build {
    context = "../../container-images/myflask"
    tag     = ["${var.myflask_image_tag}"]
  }
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset(path.module, "../container-images/myflask") : filesha1(f)]))
  }
}

resource "null_resource" "push_image" {
  triggers = {
    image_id = "${docker_image.myflask.image_id}"
  }
  provisioner "local-exec" {
    command = "minikube image load ${var.myflask_image_tag}"
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
