data "http" "client_global_ip" {
  url = "https://ifconfig.co/ip"
}

resource "aws_security_group" "http_sg" {
  name           = "http_sg"
  description = "allow http"
  vpc_id      = module.common_resources.test_vpc.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.client_global_ip.response_body)}/32"]
    #cidr_blocks = ["${data.http.client_global_ip.response_body}/32","${module.common_resources.test_instance.public_ip}/32"]
  }
}
