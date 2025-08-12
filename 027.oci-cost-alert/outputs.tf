output "budget_id" {
  description = "OCID of the created budget"
  value       = oci_budget_budget.main_budget.id
}

output "budget_display_name" {
  description = "Display name of the budget"
  value       = oci_budget_budget.main_budget.display_name
}

output "notification_topic_id" {
  description = "OCID of the notification topic"
  value       = oci_ons_notification_topic.budget_alert_topic.id
}

output "notification_topic_name" {
  description = "Name of the notification topic"
  value       = oci_ons_notification_topic.budget_alert_topic.name
}

output "email_subscription_id" {
  description = "OCID of the email subscription"
  value       = oci_ons_subscription.budget_alert_email.id
}

output "alert_rules" {
  description = "Information about created alert rules"
  value = {
    threshold_alert = {
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