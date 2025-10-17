resource "aws_ami_from_instance" "example" {
  name               = var.ami_name
  source_instance_id = aws_instance.instance.id

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}

#resource "aws_ami_from_instance" "example2" {
#  name               = "${var.ami_name}2"
#  source_instance_id = "${aws_instance.instance.id}"
#  depends_on = [
#    aws_ami_from_instance.example
#  ]
#}

resource "aws_ami_copy" "example2" {
  provider          = aws.osaka
  name              = "${var.ami_name}2"
  source_ami_id     = aws_ami_from_instance.example.id
  source_ami_region = "ap-northeast-1"

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}