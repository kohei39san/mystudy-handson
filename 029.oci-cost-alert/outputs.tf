output "budget_id" {
  description = "OCID of the created budget"
  value       = oci_budget_budget.main_budget.id
}

output "budget_display_name" {
  description = "Display name of the budget"
  value       = oci_budget_budget.main_budget.display_name
}

output "budget_amount" {
  description = "Budget amount"
  value       = oci_budget_budget.main_budget.amount
}

output "alert_rule_id" {
  description = "OCID of the budget alert rule"
  value       = oci_budget_alert_rule.budget_alert_rule.id
}

output "alert_threshold_percentage" {
  description = "Alert threshold percentage"
  value       = oci_budget_alert_rule.budget_alert_rule.threshold
}

output "alert_email_addresses" {
  description = "Email addresses configured for alerts"
  value       = var.alert_email_addresses
}