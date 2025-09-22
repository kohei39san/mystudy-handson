# Build Docker image
resource "docker_image" "mysql_init_image" {
  name = "${var.region}.ocir.io/${oci_artifacts_container_repository.mysql_init_repo.namespace}/${oci_artifacts_container_repository.mysql_init_repo.display_name}:latest"

  build {
    context    = path.module
    dockerfile = "Dockerfile"
  }

  triggers = {
    dockerfile_hash   = filemd5("${path.module}/Dockerfile")
    func_py_hash      = filemd5("${path.module}/scripts/func.py")
    requirements_hash = filemd5("${path.module}/scripts/requirements.txt")
  }
}

# Push Docker image to OCI registry
resource "docker_registry_image" "mysql_init_registry_image" {
  name = docker_image.mysql_init_image.name

  depends_on = [oci_artifacts_container_repository.mysql_init_repo]
}