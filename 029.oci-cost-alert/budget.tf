# Budget Resource
resource "oci_budget_budget" "main_budget" {
  compartment_id = var.compartment_id
  amount         = var.budget_amount
  reset_period   = var.budget_reset_period
  display_name   = var.budget_display_name
  description    = "Budget for monitoring costs and triggering alerts"

  # Target the entire compartment
  targets = [var.compartment_id]

  freeform_tags = var.freeform_tags
}

# Budget Alert Rule
resource "oci_budget_alert_rule" "budget_alert_rule" {
  budget_id      = oci_budget_budget.main_budget.id
  display_name   = "${var.budget_display_name}-Alert-Rule"
  description    = "Alert rule to notify when budget threshold is exceeded"
  type           = "ACTUAL"
  threshold      = var.alert_threshold_percentage
  threshold_type = "PERCENTAGE"

  # Recipients for the alert
  recipients = join(",", var.alert_email_addresses)

  # Message template
  message = "Budget alert: Your spending has reached ${var.alert_threshold_percentage}% of your ${var.budget_amount} budget for ${var.budget_display_name}."

  freeform_tags = var.freeform_tags
}