required_providers {
  http = {
    source  = "registry.terraform.io/hashicorp/http"
    version = ">=3.4.0"
  }
}
```
```
data "http" "client_global_ip" {
  url = "https://ifconfig.co/ip"
}

locals {
  allowed_cidr = replace("${data.http.client_global_ip.response_body}/32", "\n", "")
}

provider "aws" {
  region      = "us-west-2"
  version     = "5.19.0"
}

resource "aws_subnet" "kubectl_subnet" {
  vpc_id                  = aws_vpc.vpc.id
  map_public_ip_on_launch = true
  cidr_block              = var.instance_subnet_cidr_block
}

resource "aws_route_table_association" "kubectl_rta" {
  subnet_id      = aws_subnet.kubectl_subnet.id
  route_table_id = aws_route_table.rt.id
}

provider "http" {
  source  = "registry.terraform.io/hashicorp/http"
  version = ">=3.4.0"
}

resource "aws_security_group" "kubectl_sg" {
  vpc_id = aws_vpc.vpc.id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
