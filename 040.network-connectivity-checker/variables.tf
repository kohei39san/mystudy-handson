# ─────────────────────────────────────────────────────────────────────────────
# Common
# ─────────────────────────────────────────────────────────────────────────────

variable "project_name" {
  description = "プロジェクト名（リソース名のプレフィックスに使用）"
  type        = string
  default     = "ncc-test"
}

variable "environment" {
  description = "環境名"
  type        = string
  default     = "integration-test"
}

variable "owner" {
  description = "リソースの Owner タグ値"
  type        = string
  default     = "unknown"
}

variable "caller_ip_lookup_url" {
  description = "Terraform 実行元のグローバル IP を取得する URL"
  type        = string
  default     = "https://checkip.amazonaws.com"
}

variable "cloudrun_invoker_principal" {
  description = "Cloud Run 呼び出しを許可する principal（例: user:alice@example.com, serviceAccount:sa@project.iam.gserviceaccount.com）"
  type        = string

  validation {
    condition     = can(regex("^(user|serviceAccount|group|domain):.+", var.cloudrun_invoker_principal))
    error_message = "cloudrun_invoker_principal は user:, serviceAccount:, group:, domain: のいずれかで始まる形式で指定してください。"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# AWS
# ─────────────────────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "aws_vpc_cidr" {
  description = "AWS VPC の CIDR ブロック"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aws_subnet_cidr" {
  description = "AWS サブネットの CIDR ブロック"
  type        = string
  default     = "10.0.1.0/24"
}

variable "aws_ec2_instance_type" {
  description = "EC2 インスタンスタイプ"
  type        = string
  default     = "t3.micro"
}

variable "aws_ec2_ami" {
  description = "EC2 AMI ID（省略時は最新の Amazon Linux 2023 を自動選択）"
  type        = string
  default     = ""
}

variable "aws_rds_instance_class" {
  description = "RDS インスタンスクラス"
  type        = string
  default     = "db.t3.micro"
}

variable "aws_rds_db_name" {
  description = "RDS データベース名"
  type        = string
  default     = "testdb"
}

variable "aws_rds_username" {
  description = "RDS マスターユーザー名"
  type        = string
  default     = "admin"
}

variable "aws_rds_password" {
  description = "RDS マスターパスワード（機密情報）。terraform.tfvars または TF_VAR_aws_rds_password 環境変数で指定してください"
  type        = string
  sensitive   = true
}

# ─────────────────────────────────────────────────────────────────────────────
# Azure
# ─────────────────────────────────────────────────────────────────────────────

variable "azure_subscription_id" {
  description = "Azure サブスクリプション ID"
  type        = string
  default     = ""
}

variable "azure_location" {
  description = "Azure リージョン"
  type        = string
  default     = "japaneast"
}

variable "azure_vnet_address_space" {
  description = "Azure VNet のアドレス空間"
  type        = list(string)
  default     = ["10.1.0.0/16"]
}

variable "azure_subnet_prefix" {
  description = "Azure サブネットのアドレスプレフィックス"
  type        = list(string)
  default     = ["10.1.1.0/24"]
}

variable "azure_vm_size" {
  description = "Azure VM サイズ"
  type        = string
  default     = "Standard_B2pts_v2"
}

variable "azure_vm_admin_username" {
  description = "Azure VM 管理者ユーザー名"
  type        = string
  default     = "azureadmin"
}

variable "azure_vm_admin_password" {
  description = "Azure VM 管理者パスワード（機密情報）。terraform.tfvars または TF_VAR_azure_vm_admin_password 環境変数で指定してください"
  type        = string
  sensitive   = true
}

# ─────────────────────────────────────────────────────────────────────────────
# GCP
# ─────────────────────────────────────────────────────────────────────────────

variable "gcp_project_id" {
  description = "GCP プロジェクト ID"
  type        = string
  default     = ""
}

variable "gcp_region" {
  description = "GCP リージョン"
  type        = string
  default     = "asia-northeast1"
}

variable "gcp_zone" {
  description = "GCP ゾーン"
  type        = string
  default     = "asia-northeast1-a"
}

variable "gcp_vm_machine_type" {
  description = "GCP VM マシンタイプ"
  type        = string
  default     = "e2-micro"
}

variable "gcp_vm_image" {
  description = "GCP VM イメージ"
  type        = string
  default     = "debian-cloud/debian-12"
}

variable "gcp_cloudrun_image" {
  description = "Cloud Run コンテナイメージ"
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "gcp_cloudsql_database_version" {
  description = "Cloud SQL データベースバージョン"
  type        = string
  default     = "MYSQL_8_0"
}

variable "gcp_cloudsql_tier" {
  description = "Cloud SQL インスタンス Tier"
  type        = string
  default     = "db-f1-micro"
}

variable "gcp_cloudsql_disk_size" {
  description = "Cloud SQL ディスクサイズ (GB)"
  type        = number
  default     = 10
}
