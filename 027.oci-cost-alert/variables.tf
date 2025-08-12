variable "region" {
  description = "OCIリージョン"
  type        = string
  default     = "ap-osaka-1"
}

variable "compartment_id" {
  description = "コンパートメントOCID"
  type        = string
}

variable "alert_email" {
  description = "アラート通知先メールアドレス"
  type        = string
}

variable "budget_amount" {
  description = "予算金額"
  type        = number
  default     = 100
}

variable "budget_currency" {
  description = "予算通貨"
  type        = string
  default     = "USD"
}

variable "alert_threshold_percentage" {
  description = "アラート閾値（パーセンテージ）"
  type        = number
  default     = 80
  validation {
    condition     = var.alert_threshold_percentage > 0 && var.alert_threshold_percentage <= 100
    error_message = "アラート閾値は1から100の間で設定してください。"
  }
}

variable "budget_display_name" {
  description = "予算の表示名"
  type        = string
  default     = "Monthly Budget Alert"
}

variable "notification_topic_name" {
  description = "通知トピック名"
  type        = string
  default     = "budget-alert-topic"
}

variable "freeform_tags" {
  description = "フリーフォームタグ"
  type        = map(string)
  default = {
    Environment = "Production"
    ManagedBy   = "Terraform"
    Terraform   = "true"
  }
}