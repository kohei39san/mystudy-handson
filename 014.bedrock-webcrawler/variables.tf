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
  description = "クローラー実行のスケジュール (cron形式)"
  type        = string
  default     = "cron(0 0 ? * SUN *)" # 毎週日曜日の午前0時に実行
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

variable "default_tags" {
  description = "デフォルトのリソースタグ"
  type        = map(string)
  default     = {
    Environment = "Production"
    Project     = "BedrockWebCrawler"
    ManagedBy   = "Terraform"
  }
}

variable "bedrock_model_arn" {
  description = "BedrockのEmbeddingモデルARN"
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "crawler_scope" {
  description = "Bedrockウェブクローラーのスコープ"
  type        = string
  default     = "HOST_ONLY"
}
