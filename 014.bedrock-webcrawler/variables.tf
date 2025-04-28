variable "aws_region" {
  description = "AWSリージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "crawling_urls" {
  description = "クロール対象のURLリスト"
  type        = list(string)
  default     = ["https://aws.amazon.com/jp/about-aws/whats-new/recent/feed/"]
}

variable "crawling_interval" {
  description = "クローラー実行のスケジュール"
  type        = string
  default     = "rate(7 days)"
}

variable "opensearch_instance_type" {
  description = "OpenSearchインスタンスタイプ"
  type        = string
  default     = "t3.small.search"
}

variable "bedrock_max_tokens" {
  description = "Bedrockモデルの最大トークン数"
  type        = number
  default     = 4096
}

variable "project_name" {
  description = "プロジェクト名"
  type        = string
  default     = "bedrock-webcrawler"
}
