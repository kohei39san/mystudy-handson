resource "docker_image" "nginx_lb" {
  name = "nginx-lb"
  build {
    context = "../../container-images/nginx-lb"
    tag     = ["${var.nginx_lb_image_tag}"]
  }
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset(path.module, "../container-images/nginx-lb") : filesha1(f)]))
  }
}

resource "docker_container" "nginx_lb" {
  name  = "nginx-lb"
  image = docker_image.nginx_lb.image_id

  ports {
    internal = "80"
    external = "80"
  }

  networks_advanced {
    name = "minikube"
  }

  dns        = ["10.96.0.10"]
  dns_search = ["svc.cluster.local", "cluster.local"]
  privileged = true
}

resource "null_resource" "route_nginx_lb" {
  triggers = {
    id = "${docker_container.nginx_lb.id}"
  }
  provisioner "local-exec" {
    command = "docker exec nginx-lb route add -net 10.96.0.0 netmask 255.240.0.0 gw 192.168.49.2 eth0"
  }
}
