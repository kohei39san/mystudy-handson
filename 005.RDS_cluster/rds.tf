locals {
  identifier = replace("db${var.aws_tags["Name"]}", "/[^a-zA-Z0-9-]/", "")
}

resource "aws_db_subnet_group" "example" {
  name       = "db-subnet-group${var.aws_tags["Name"]}"
  subnet_ids = [aws_subnet.example_subnet1.id, aws_subnet.example_subnet2.id]
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}

resource "aws_rds_cluster" "rds_cluster" {
  cluster_identifier      = local.identifier
  engine                  = "aurora-mysql"
  engine_version          = "8.0.mysql_aurora.3.05.2"
  database_name           = "mydb"
  master_username         = "foo"
  master_password         = "must_be_eight_characters"
  db_subnet_group_name    = aws_db_subnet_group.example.name
  backup_retention_period = 1
  preferred_backup_window = "07:00-09:00"
  skip_final_snapshot     = true
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}

resource "aws_rds_cluster_instance" "cluster_instances" {
  count                = 1
  identifier           = "${local.identifier}-${count.index}"
  cluster_identifier   = aws_rds_cluster.rds_cluster.id
  instance_class       = "db.t3.medium"
  engine               = aws_rds_cluster.rds_cluster.engine
  engine_version       = aws_rds_cluster.rds_cluster.engine_version
  db_subnet_group_name = aws_db_subnet_group.example.name
  
  tags = merge(
    var.aws_tags,
    {
      Environment = "dev",
      Terraform   = "true"
    }
  )
}