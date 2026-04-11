# ─────────────────────────────────────────────────────────────────────────────
# AWS リソース: VPC / Subnet / Security Group / EC2 / RDS
# ─────────────────────────────────────────────────────────────────────────────

# --- VPC ---

resource "aws_vpc" "main" {
  cidr_block           = var.aws_vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# --- Internet Gateway ---

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# --- Subnet（パブリック）---

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.aws_subnet_cidr
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet"
    Tier = "public"
  }
}

# --- Subnet（プライベート: RDS 用）---

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}c"

  tags = {
    Name = "${var.project_name}-private-subnet"
    Tier = "private"
  }
}

# --- Route Table (パブリック) ---

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# --- Security Group (EC2 用: 接続許可・拒否パターンを両方定義) ---
# ingress: HTTP(80), HTTPS(443), SSH(22) を 0.0.0.0/0 から許可 → internet_reachability=reachable

resource "aws_security_group" "ec2" {
  name        = "${var.project_name}-ec2-sg"
  description = "Security group for EC2 integration test instance"
  vpc_id      = aws_vpc.main.id

  # HTTP 許可（接続許可パターン: internet_reachability=reachable を確認するためのテスト用ルール）
  # tfsec:ignore:aws-ec2-no-public-ingress-sgr
  ingress {
    description = "Allow HTTP - integration test only, not for production use"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS 許可（接続許可パターン: internet_reachability=reachable を確認するためのテスト用ルール）
  # tfsec:ignore:aws-ec2-no-public-ingress-sgr
  ingress {
    description = "Allow HTTPS - integration test only, not for production use"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH 許可（接続許可パターン: internet_reachability=reachable を確認するためのテスト用ルール）
  # tfsec:ignore:aws-ec2-no-public-ingress-sgr
  ingress {
    description = "Allow SSH - integration test only, not for production use"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress: 全許可
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ec2-sg"
  }
}

# --- Security Group (RDS 用: VPC 内からのみ MySQL 許可) ---
# publicly_accessible=false → internet_reachability=not_reachable, private_reachability=reachable

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS integration test instance"
  vpc_id      = aws_vpc.main.id

  # MySQL/Aurora 許可（VPC 内のみ）
  ingress {
    description = "Allow MySQL from VPC"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.aws_vpc_cidr]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

# --- AMI: 最新の Amazon Linux 2023 を自動取得 ---

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  ec2_ami = var.aws_ec2_ami != "" ? var.aws_ec2_ami : data.aws_ami.amazon_linux_2023.id
}

# --- EC2 Instance（パブリックサブネット + パブリック IP あり → internet_reachability=reachable）---

resource "aws_instance" "test" {
  ami                         = local.ec2_ami
  instance_type               = var.aws_ec2_instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.ec2.id]
  associate_public_ip_address = true

  tags = {
    Name = "${var.project_name}-ec2"
  }
}

# --- DB Subnet Group（RDS 用マルチ AZ サブネットグループ）---

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.public.id, aws_subnet.private.id]

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# --- RDS Instance（プライベートアクセスのみ → internet_reachability=not_reachable）---

resource "aws_db_instance" "test" {
  identifier             = "${var.project_name}-rds"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = var.aws_rds_instance_class
  allocated_storage      = 20
  db_name                = var.aws_rds_db_name
  username               = var.aws_rds_username
  password               = var.aws_rds_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  skip_final_snapshot    = true
  deletion_protection    = false
  multi_az               = false

  tags = {
    Name = "${var.project_name}-rds"
  }
}
