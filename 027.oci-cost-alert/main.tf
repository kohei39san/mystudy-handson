# Notification Topic for Budget Alerts
resource "oci_ons_notification_topic" "budget_alert_topic" {
  compartment_id = var.compartment_id
  name           = var.notification_topic_name
  description    = "Notification topic for budget alerts"
  freeform_tags  = var.freeform_tags
}

# Email Subscription for Budget Alerts
resource "oci_ons_subscription" "budget_alert_email" {
  compartment_id = var.compartment_id
  topic_id       = oci_ons_notification_topic.budget_alert_topic.id
  protocol       = "EMAIL"
  endpoint       = var.alert_email
  freeform_tags  = var.freeform_tags
}

# Budget Resource
resource "oci_budget_budget" "main_budget" {
  compartment_id   = var.compartment_id
  amount           = var.budget_amount
  reset_period     = "MONTHLY"
  display_name     = var.budget_display_name
  description      = "Monthly budget with alert notifications"
  budget_processing_period_start_offset = 1
  
  # Target the entire compartment
  targets = [var.compartment_id]
  
  freeform_tags = var.freeform_tags
}

# Budget Alert Rule
resource "oci_budget_alert_rule" "budget_alert" {
  budget_id    = oci_budget_budget.main_budget.id
  type         = "ACTUAL"
  threshold    = var.alert_threshold_percentage
  threshold_type = "PERCENTAGE"
  display_name = "Budget Alert at ${var.alert_threshold_percentage}%"
  description  = "Alert when budget reaches ${var.alert_threshold_percentage}% of allocated amount"
  message      = "Budget alert: You have reached ${var.alert_threshold_percentage}% of your monthly budget of ${var.budget_amount} ${var.budget_currency}"
  
  recipients = oci_ons_notification_topic.budget_alert_topic.topic_id
  
  freeform_tags = var.freeform_tags
}

# Additional Alert Rule for 100% threshold
resource "oci_budget_alert_rule" "budget_alert_100" {
  budget_id    = oci_budget_budget.main_budget.id
  type         = "ACTUAL"
  threshold    = 100
  threshold_type = "PERCENTAGE"
  display_name = "Budget Alert at 100%"
  description  = "Alert when budget reaches 100% of allocated amount"
  message      = "Budget alert: You have reached 100% of your monthly budget of ${var.budget_amount} ${var.budget_currency}"
  
  recipients = oci_ons_notification_topic.budget_alert_topic.topic_id
  
  freeform_tags = var.freeform_tags
}

# Forecast Alert Rule (optional - alerts when forecasted to exceed budget)
resource "oci_budget_alert_rule" "budget_forecast_alert" {
  budget_id    = oci_budget_budget.main_budget.id
  type         = "FORECAST"
  threshold    = 100
  threshold_type = "PERCENTAGE"
  display_name = "Budget Forecast Alert"
  description  = "Alert when forecasted to exceed budget"
  message      = "Budget forecast alert: You are forecasted to exceed your monthly budget of ${var.budget_amount} ${var.budget_currency}"
  
  recipients = oci_ons_notification_topic.budget_alert_topic.topic_id
  
  freeform_tags = var.freeform_tags
}