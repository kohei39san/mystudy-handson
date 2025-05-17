variable "rss_feed_url" {
  type    = string
  default = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"
}
variable "summary_prompt" {
  type    = string
  default = <<-EOT
    AWSの新機能の追加を優先事項として、サービスごとに分類して要約してください。
    以下のカテゴリに分けて整理してください：
    1. コンピューティング（EC2, Lambda, ECS, EKSなど）
    2. ストレージ（S3, EBS, EFSなど）
    3. データベース（RDS, DynamoDB, Redshiftなど）
    4. ネットワーキング（VPC, Route 53, CloudFrontなど）
    5. 機械学習・AI（SageMaker, Bedrock, Rekognitionなど）
    6. セキュリティ（IAM, GuardDuty, Security Hubなど）
    7. その他の重要な更新
    
    各カテゴリでは、最も重要な新機能や改善点を簡潔に説明してください。
    特に以下の点に注目してください：
    - 新しいサービスや機能のリリース
    - 既存サービスの大幅な機能強化
    - コスト削減につながる変更
    
    形式は以下の通りとしてください。
    - 要約は2000文字以内にしてください。
    - 過去7日分の情報としてください。
    - カテゴリ名は「# *任意のカテゴリ名* 」としてください。
    - リンクURLは<任意のURL|「表示するテキスト」>としてください。
    - リストは「•」を行頭につけてください。
  EOT
}
variable "schedule_expression" {
  type    = string
  default = "cron(0 0 ? * MON *)"
}
variable "lambda_timeout" {
  type    = number
  default = 300
}
variable "lambda_memory_size" {
  type    = number
  default = 256
}

variable "aws_region" {
  type    = string
  default = "ap-northeast-1"
}

variable "openrouter_api_key_param" {
  type    = string
  default = "/rss-summary/openrouter-api-key"
}

variable "slack_webhook_url_param" {
  type    = string
  default = "/rss-summary/slack-webhook-url"
}
