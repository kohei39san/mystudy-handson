data "http" "client_global_ip" {
  url = "https://ifconfig.co/ip"
}

resource "aws_security_group" "http_sg" {
  ingress {
    from_port = 0
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["${chomp(data.http.client_global_ip.response_body)}/32"]
    #cidr_blocks = ["${data.http.client_global_ip.response_body}/32","${module.common_resources.test_instance.public_ip}/32"]
  }
}
