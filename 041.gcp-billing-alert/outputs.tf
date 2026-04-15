output "budget_id" {
  description = "ID of the created billing budget"
  value       = google_billing_budget.main_budget.id
}

output "budget_display_name" {
  description = "Display name of the budget"
  value       = google_billing_budget.main_budget.display_name
}

output "budget_amount" {
  description = "Budget amount"
  value       = var.budget_amount
}

output "alert_threshold_percentages" {
  description = "Alert threshold percentages configured"
  value       = var.alert_threshold_percentages
}

output "notification_channel_ids" {
  description = "IDs of the monitoring notification channels"
  value       = google_monitoring_notification_channel.email[*].id
}

output "alert_email_addresses" {
  description = "Email addresses configured for alerts"
  value       = var.alert_email_addresses
}
