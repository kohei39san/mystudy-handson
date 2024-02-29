data "http" "client_global_ip" {
  url = "https://ifconfig.co/ip"
}

resource "aws_security_group" "prometheus_sg" {
  name        = "http_sg"
  description = "allow access to prometheus"
  vpc_id      = module.common_resources.vpc.id
  ingress {
    from_port   = 30100
    to_port     = 30100
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.client_global_ip.response_body)}/32"]
  }
  ingress {
    from_port   = 30200
    to_port     = 30200
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.client_global_ip.response_body)}/32"]
  }
  ingress {
    from_port   = 30300
    to_port     = 30300
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.client_global_ip.response_body)}/32"]
  }
}
