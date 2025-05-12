variable "aws_region" {
  description = "AWSリージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "crawling_url" {
  description = "クロール対象のURL"
  type        = string
  default     = "https://aws.amazon.com/jp/about-aws/whats-new/recent/feed/"
}

variable "crawling_interval" {
  description = "クローラー実行のスケジュール (cron式)"
  type        = string
  default     = "cron(0 0 ? * MON *)" # 毎週月曜日の午前0時に実行
}

variable "opensearch_instance_type" {
  description = "OpenSearchインスタンスタイプ"
  type        = string
  default     = "t3.small.search"
}

variable "project_name" {
  description = "プロジェクト名"
  type        = string
  default     = "bedrock-webcrawler"
}

variable "tags" {
  description = "リソースに付与するタグ"
  type        = map(string)
  default = {
    Environment = "Production"
    Project     = "BedrockWebCrawler"
    ManagedBy   = "Terraform"
  }
}

variable "bedrock_model_arn" {
  description = "Bedrockのモデル ARN"
  type        = string
  default     = "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0"
}

variable "crawler_scope" {
  description = "Bedrockウェブクローラーのスコープ"
  type        = string
  default     = "HOST_ONLY"
}
