# 会話履歴を保存するDynamoDBテーブル
resource "aws_dynamodb_table" "conversation_history" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST" # オンデマンドキャパシティモード（最小コスト）
  hash_key     = "userId"
  range_key    = "channelId"

  attribute {
    name = "userId"
    type = "S"
  }

  attribute {
    name = "channelId"
    type = "S"
  }

  # 項目の有効期限（TTL）を設定
  ttl {
    attribute_name = "expirationTime"
    enabled        = true
  }

  # ポイントインタイムリカバリ（PITR）を無効化（コスト削減）
  point_in_time_recovery {
    enabled = false
  }

  tags = {
    Name        = var.dynamodb_table_name
    Environment = "production"
    Project     = var.project_name
  }
}