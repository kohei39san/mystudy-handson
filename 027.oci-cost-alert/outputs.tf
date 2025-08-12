output "budget_id" {
  description = "予算のOCID"
  value       = oci_budget_budget.main_budget.id
}

output "budget_display_name" {
  description = "予算の表示名"
  value       = oci_budget_budget.main_budget.display_name
}

output "notification_topic_id" {
  description = "通知トピックのOCID"
  value       = oci_ons_notification_topic.budget_alert_topic.id
}

output "notification_topic_name" {
  description = "通知トピック名"
  value       = oci_ons_notification_topic.budget_alert_topic.name
}

output "email_subscription_id" {
  description = "メール購読のOCID"
  value       = oci_ons_subscription.budget_alert_email.id
}

output "alert_rules" {
  description = "作成されたアラートルールの情報"
  value = {
    percentage_alert = {
      id           = oci_budget_alert_rule.budget_alert.id
      display_name = oci_budget_alert_rule.budget_alert.display_name
      threshold    = oci_budget_alert_rule.budget_alert.threshold
    }
    full_budget_alert = {
      id           = oci_budget_alert_rule.budget_alert_100.id
      display_name = oci_budget_alert_rule.budget_alert_100.display_name
      threshold    = oci_budget_alert_rule.budget_alert_100.threshold
    }
    forecast_alert = {
      id           = oci_budget_alert_rule.budget_forecast_alert.id
      display_name = oci_budget_alert_rule.budget_forecast_alert.display_name
      threshold    = oci_budget_alert_rule.budget_forecast_alert.threshold
    }
  }
}

output "budget_amount" {
  description = "設定された予算金額"
  value       = var.budget_amount
}

output "budget_currency" {
  description = "予算通貨"
  value       = var.budget_currency
}

output "alert_email" {
  description = "アラート通知先メールアドレス"
  value       = var.alert_email
  sensitive   = true
}