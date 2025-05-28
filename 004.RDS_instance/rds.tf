locals {
  identifier = replace("db${var.aws_tags["Name"]}", "/[^a-zA-Z0-9-]/", "")
}

resource "aws_db_subnet_group" "example" {
  name       = "db-subnet-group${var.aws_tags["Name"]}"
  subnet_ids = [aws_subnet.example_subnet1.id, aws_subnet.example_subnet2.id]

  tags = {
    Name        = "db-subnet-group"
    Environment = var.environment
    Terraform   = "true"
  }
}

resource "aws_db_instance" "example" {
  allocated_storage      = 20
  storage_type           = "gp3"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  identifier             = local.identifier
  username               = "admin"
  password               = "password"
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.example_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.example.name

  tags = {
    Name        = "db-instance"
    Environment = var.environment
    Terraform   = "true"
  }
}