output "budget_id" {
  description = "ID of the created budget"
  value       = azurerm_consumption_budget_subscription.main.id
}

output "budget_name" {
  description = "Name of the budget"
  value       = azurerm_consumption_budget_subscription.main.name
}

output "budget_amount" {
  description = "Budget amount"
  value       = azurerm_consumption_budget_subscription.main.amount
}

output "actual_alert_thresholds" {
  description = "Actual cost alert thresholds configured"
  value       = var.actual_alert_thresholds
}

output "forecasted_alert_threshold" {
  description = "Forecasted cost alert threshold configured"
  value       = var.forecasted_alert_threshold
}

output "action_group_id" {
  description = "ID of the Action Group used for notifications"
  value       = azurerm_monitor_action_group.billing_alert.id
}

output "action_group_name" {
  description = "Name of the Action Group"
  value       = azurerm_monitor_action_group.billing_alert.name
}

output "alert_email_addresses" {
  description = "Email addresses configured for alerts"
  value       = var.alert_email_addresses
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}
